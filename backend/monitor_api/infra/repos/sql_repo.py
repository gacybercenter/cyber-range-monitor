


import logging
from typing import Any, Generic, TypeVar
from venv import logger

from pydantic import BaseModel
from sqlalchemy import MappingResult, Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

# from sqlalchemy.sql.selectable
M = TypeVar('M', bound=DeclarativeBase)


S = TypeVar('S', bound=BaseModel)


class SqlTransactionMixin(Generic[M]):
    '''
    A simple mixin for SQLAlchemy repositories that provides
    basic session utilities.
    '''
    model: type[M]

    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def mappings(self, statement: Select) -> MappingResult:
        '''
        Execute a statement and return the result as mappings.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        MappingResult
        '''
        result = await self.db.execute(statement)
        return result.mappings()

    async def all(self, statement: Select) -> list[M]:
        '''
        Execute a statement and return all results as a list of models.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        list[M]
        '''
        result = await self.db.execute(statement)
        return list(result.scalars().all()) or []

    async def write(self, *, commit: bool = True):
        '''
        Flushes the current session, and optionally commits
        the transaction.

        Parameters
        ----------
        commit : bool, optional
            _whether to commit the transaction_, by default True
        '''
        if commit:
            await self.db.commit()
        else:
            await self.db.flush()

    async def stream_mappings(self, statement: Select):
        '''
        Stream results of a statement as mappings.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        _dict_
            _The mappings of the models returned_
        '''
        result = await self.db.stream(statement)
        async for row in result.mappings():
            yield dict(row)

    async def one_or_none(self, statement: Select) -> M | None:
        '''
        Execute a statement and return one result or None.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        M | None
            _The model or none_
        '''
        result = await self.db.execute(statement)
        return result.scalars().one_or_none()



class SqlRepo(SqlTransactionMixin[M], Generic[M]):
    """
    Simple generic repository for SQLAlchemy models with basic
    CRUD abstractions. You must set the `model` attribute when
    subclassing this repository.
    """
    model: type[M]

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.logger = logging.getLogger(__name__)

    @property
    def model_name(self) -> str:
        '''
        The name of the model.

        Returns
        -------
        str
            _The model name_
        '''
        return self.model.__name__


    def new(self, **kwargs) -> M:
        '''
        Create a new model instance with the provided keyword arguments
        and add it to the current session and flushes the session.

        Returns
        -------
        M
            _The model model_
        '''
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.logger.info(f'Created new {self.model_name} instance.')
        return instance

    async def create(self, **kwargs) -> M | None:
        '''
        Create a new model instance with the provided keyword arguments,
        adds it to the current session and flushes the session.
        Returns None if there was an error.

        Returns
        -------
        M | None
            _The model instance or None if there was an error_
        '''
        obj = self.new(**kwargs)
        await self.db.flush()
        return obj

    async def remove(self, model: M, *, flush: bool = True) -> bool:
        '''
        Remove a model instance from the current session and flushes
        the session. Returns False if there was an error.

        Parameters
        ----------
        model : M
            _The model to remove_

        Returns
        -------
        bool
            _Whether the model was successfully removed_
        '''
        model_id = getattr(model, 'id', None) or 'unknown'
        self.logger.info(f'Removing instance {model} from `{self.model_name}` ')
        try:
            await self.db.delete(model)
        except Exception as e:
            logger.error(
                f'Error removing {model} instance with id {model_id}',
                exc_info=e
            )
            return False
        if flush:
            await self.db.flush()
        return True

    async def edit(
        self,
        model: M,
        **kwargs
    ) -> M | None:
        '''
        Edits a model instance with the provided keyword arguments,
        returns None of there was an error.

        Parameters
        ----------
        model : M
            _The model to edit_
        **kwargs
            _The fields to update with their new values_
        Returns
        -------
        M | None
            _The updated model or None if there was an error_
        '''
        model_id = getattr(model, 'id', None) or 'unknown'
        self.logger.info(f'Editing {model}...')
        try:
            for key, value in kwargs.items():
                setattr(model, key, value)
        except Exception as e:
            logger.error(
                f'Error editing {self.model_name} instance {model_id}',
                exc_info=e
            )
            return None

        self.db.add(model)
        logger.debug('successfully edited model, flushing to session...')
        await self.db.flush()
        return model

    async def count(self, predicate: Any) -> int:
        '''
        Count the number of records for a given predicate.

        Parameters
        ----------
        predicate : Any
            _The where clause to count by_

        Returns
        -------
        int
        '''
        query = select(func.count()).select_from(self.model).where(predicate)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() or 0

    async def exists(self, predicate: Any) -> bool:
        '''
        Check if a record exists for a given predicate.

        Parameters
        ----------
        predicate : Any
            _the where clause_

        Returns
        -------
        bool
        '''
        query = select(func.count()).select_from(self.model).where(predicate)
        result = await self.db.execute(query)
        count = result.scalar_one_or_none() or 0
        return count > 0

    async def count_total(self, statement: Select) -> int:
        '''
        Get the total count of records for a given query.

        Parameters
        ----------
        statement : Select
        offset : int, optional
            _The offset_, by default 0
        limit : int, optional
            _The max models_, by default 10

        Returns
        -------
        int
        '''
        count_stmnt = select(func.count()).select_from(self.model)
        if statement._whereclause is not None:
            count_stmnt = count_stmnt.where(statement._whereclause)
        total_result = await self.db.execute(count_stmnt)
        return total_result.scalar_one_or_none() or 0

    async def list_models(self, statement: Select, *, limit: int = 50) -> list[M]:
        '''
        List all records for a given query.

        Parameters
        ----------
        statement : Select
        limit : int, optional
            _The max records to return_, by default 50

        Returns
        -------
        list[M]
            _The models returned_
        '''
        limit = max(limit, 1)
        result = await self.db.execute(statement.limit(limit))
        return list(result.scalars().all()) or []

    async def list_mappings(self, statement: Select, *, limit: int = 50) -> list[dict]:
        '''
        List all records for a given query as mappings.

        Parameters
        ----------
        statement : Select
        limit : int, optional
            _Max records to return_, by default 50

        Returns
        -------
        list[dict]
            _List of the mappings_
        '''
        limit = max(limit, 1)
        result = await self.db.execute(statement.limit(limit))
        return [dict(row) for row in result.mappings().all()] or []


    async def save(self) -> bool:
        '''
        Commits the current transaction, returns True if successful,

        Returns
        -------
        bool
        '''
        try:
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
