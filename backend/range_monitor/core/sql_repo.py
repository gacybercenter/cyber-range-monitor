import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from venv import logger

from sqlalchemy import MappingResult, Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.expression import ColumnElement

if TYPE_CHECKING:
    from range_monitor.core.pydantic import PydanticMixin

# from sqlalchemy.sql.selectable
M = TypeVar('M', bound=DeclarativeBase)


S = TypeVar('S', bound='PydanticMixin')


class SqlTransactionMixin(Generic[M]):
    """
    A simple mixin for SQLAlchemy repositories that provides
    basic session utilities.
    """

    model: type[M]

    def __init__(self, db: AsyncSession) -> None:
        self.db: AsyncSession = db

    async def mappings(self, statement: Select) -> MappingResult:
        """
        Execute a statement and return the result as mappings.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        MappingResult
        """
        result = await self.db.execute(statement)
        return result.unique().mappings()

    async def all(self, statement: Select) -> list[M]:
        """
        Execute a statement and return all results as a list of models.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        list[M]
        """
        result = await self.db.execute(statement)
        return list(result.unique().scalars().all()) or []

    async def stream_mappings(self, statement: Select):
        """
        Stream results of a statement as mappings.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        _dict_
            _The mappings of the models returned_
        """
        result = await self.db.stream(statement)
        async for row in result.unique().mappings():
            yield dict(row)

    async def stream(self, statement: Select):
        """
        Stream results of a statement as models.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        M
            _The models returned_
        """
        result = await self.db.stream(statement)
        async for row in result.unique().scalars():
            yield row

    async def one_or_none(self, statement: Select) -> M | None:
        """
        Execute a statement and return one result or None.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        M | None
            _The model or none_
        """
        result = await self.db.execute(statement)
        return result.scalars().one_or_none()

    async def first(self, statement: Select) -> M | None:
        """
        Execute a statement and return the first result or None.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        M | None
            _The model or none_
        """
        result = await self.db.execute(statement)
        return result.scalars().first()

    async def save(self) -> bool:
        """
        Commits the current transaction, returns True if successful,

        Returns
        -------
        bool
        """
        try:
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False


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
    def table_name(self) -> str:
        return self.model.__tablename__

    def create(self, **kwargs) -> M:
        """
        Create a new model instance with the provided keyword arguments
        and add it to the current session and flushes the session.
        Note: Could raise an exception if the parameters are invalid.

        Returns
        -------
        M
            _The model model_
        """
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.logger.info(f'Created new {self.table_name} instance.')
        return instance

    async def get(self, entity_id: str) -> M | None:
        """
        Read a model instance by its ID, returns None if not found.

        Parameters
        ----------
        entity_id : UUID
            _The ID of the model to read_

        Returns
        -------
        M | None
            _The model instance or None if not found_
        """
        return await self.db.get(self.model, entity_id)

    async def update(self, model: M, params: dict, *, refresh: bool = True) -> M | None:
        """
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
        """
        model_id = getattr(model, 'id', None) or 'unknown'
        self.logger.info(f'Editing {model}...')
        try:
            for key, value in params.items():
                setattr(model, key, value)
        except Exception as e:
            logger.error(
                f'Error editing {self.table_name} instance {model_id}', exc_info=e
            )
            return None

        self.db.add(model)
        logger.debug('successfully edited model, flushing to session...')
        await self.save()
        if refresh:
            await self.db.refresh(model)
        return model

    async def delete(self, model: M, *, auto_commit: bool = True) -> bool:
        """
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
        """
        self.logger.info(f'Removing instance {model} from `{self.table_name}` ')
        try:
            await self.db.delete(model)
        except Exception as e:
            logger.error(f'Error removing {model}', exc_info=e)
            return False

        if auto_commit:
            return await self.save()

        return True

    async def count(self, predicate: Any) -> int:
        """
        Count the number of records for a given predicate.

        Parameters
        ----------
        predicate : Any
            _The where clause to count by_

        Returns
        -------
        int
        """
        query = select(func.count()).select_from(self.model).where(predicate)
        result = await self.db.execute(query)
        return result.scalar_one_or_none() or 0

    async def get_query_total(self, statement: Select) -> int:
        """
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
        """
        count_stmnt = select(func.count()).select_from(self.model)
        if statement._whereclause is not None:
            count_stmnt = count_stmnt.where(statement._whereclause)

        total_result = await self.db.execute(count_stmnt)
        return total_result.scalar_one_or_none() or 0

    async def list_all(self, statement: Select, *, limit: int = 50) -> list[M]:
        """
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
        """
        limit = max(limit, 1)
        result = await self.db.execute(statement.limit(limit))
        return list(result.scalars().all()) or []

    async def batch_update(self, values: dict, *where_clauses: ColumnElement) -> int:
        """
        Batch update records matching the where clauses with the provided values.

        Parameters
        ----------
        *where_clauses
            _The where clauses to match_
        **values
            _The values to update_

        Returns
        -------
        int
            _The number of rows updated_
        """
        stmt = update(self.model).where(*where_clauses).values(**values)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount or 0

    def select(self) -> Select:
        """
        Create a basic select statement for the model.

        Returns
        -------
        Select
        """
        return select(self.model)