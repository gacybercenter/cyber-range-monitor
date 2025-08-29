


import logging
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from venv import logger

from sqlalchemy import MappingResult, Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, InstrumentedAttribute
from sqlalchemy.sql.expression import ColumnElement

if TYPE_CHECKING:
    from range_monitor.core.pydantic import PydanticMixin

# from sqlalchemy.sql.selectable
M = TypeVar('M', bound=DeclarativeBase)


S = TypeVar('S', bound='PydanticMixin')


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
        return result.unique().mappings()

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
        return list(result.unique().scalars().all()) or []

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
        async for row in result.unique().mappings():
            yield dict(row)

    async def stream(self, statement: Select):
        '''
        Stream results of a statement as models.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        M
            _The models returned_
        '''
        result = await self.db.stream(statement)
        async for row in result.unique().scalars():
            yield row

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

    async def first(self, statement: Select) -> M | None:
        '''
        Execute a statement and return the first result or None.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        M | None
            _The model or none_
        '''
        result = await self.db.execute(statement)
        return result.scalars().first()


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

    @property
    def read(self) -> Select:
        '''
        A select statement for reading all models.

        Returns
        -------
        Select[M]
            _The select statement_
        '''
        return select(self.model)

    def insert(self, **kwargs) -> M:
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


    async def create(self, params: dict, *, auto_commit: bool = True) -> M | None:
        '''
        Create a new model instance with the provided keyword arguments,
        adds it to the current session and flushes the session.
        Returns None if there was an error.

        Returns
        -------
        M | None
            _The model instance or None if there was an error_
        '''
        obj = self.insert(**params)
        if auto_commit:
            await self.save()
        return obj

    async def get_entity(self, entity_id: str) -> M | None:
        '''
        Read a model instance by its ID, returns None if not found.

        Parameters
        ----------
        entity_id : UUID
            _The ID of the model to read_

        Returns
        -------
        M | None
            _The model instance or None if not found_
        '''
        return await self.db.get(self.model, entity_id)

    async def update(self, model: M, **kwargs) -> M | None:
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
            for key, value in kwargs.items():
                setattr(model, key, value)
        except Exception as e:
            logger.error(
                f'Error editing {self.model_name} instance {model_id}', exc_info=e
            )
            return None

        self.db.add(model)
        logger.debug('successfully edited model, flushing to session...')
        await self.save()
        await self.db.refresh(model)
        return model


    async def delete(self, model: M, *, auto_commit: bool = True) -> bool:
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

        if auto_commit:
            return await self.save()

        return True

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

    async def count_total_rows(self, statement: Select) -> int:
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

    async def batch_update(self, values: dict, *where_clauses: ColumnElement) -> int:
        '''
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
        '''
        stmt = update(self.model).where(*where_clauses).values(**values)
        result = await self.db.execute(stmt)
        await self.db.flush()
        return result.rowcount or 0

    async def stream_query(self, statement: Select, *, schema: type[S]) :
        '''
        Streams results of a query and yields them as the provided schema
        or data transfer object.


        Parameters
        ----------
        statement : Select
        schema : type[S]
        '''
        async for mapping in self.stream(statement):
            try:
                yield schema.convert(mapping)
            except Exception as e:
                self.logger.error(
                    f'Error generating schema for {self.model_name}: {e}',
                    exc_info=e
                )

    async def query_to_schemas(self, statement: Select, *, schema: type[S]) -> list[S]:
        '''
        Execute a query and return the results as a list of the provided schema
        or data transfer object.

        Parameters
        ----------
        statement : Select
        schema : type[S]

        Returns
        -------
        list[S]
            _The list of schemas_
        '''
        items: list[S] = []
        async for cols in self.stream_mappings(statement):
            try:
                items.append(schema.convert(cols))
            except Exception as e:
                self.logger.error(
                    f'Error generating schema for {self.model_name}: {e}',
                    exc_info=e
                )
        return items

    def select(
        self,
        *where: ColumnElement,
        cols: tuple[ColumnElement | InstrumentedAttribute, ...],
    ) -> Select:
        '''
        Create a select statement for the given columns and where clauses.

        Parameters
        ----------
        cols : tuple[ColumnElement, ...]
            _The columns to select_

        Returns
        -------
        Select
            _The select statement_
        '''
        return select(*cols).select_from(self.model).where(*where)

    async def query_cols(
        self,
        cols: tuple[ColumnElement, ...],
        *where: ColumnElement
    ) -> list[dict]:
        '''
        Query the given columns and return the results as a list of mappings.

        Parameters
        ----------
        cols : tuple[ColumnElement, ...]
            _The columns to select_
        *where : ColumnElement
            _The where clauses_

        Returns
        -------
        list[dict]
            _The list of mappings_
        '''
        statement = self.select(cols=cols, *where)
        return await self.list_mappings(statement)