'''
A generic SQL repository using SQLAlchemy async sessions
with utility functions for executing select statements

Raises
------
ValueError
    If no model is provided as a parameter or defined in class
'''
import logging
from typing import Any, AsyncGenerator, Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from range_monitor.infra import sql_cmds

M = TypeVar('M', bound=DeclarativeBase | Any)
logger = logging.getLogger(__name__)



class SQLRepository(Generic[M]):
    model: type[M]

    def __init__(
        self,
        db: AsyncSession,
        *,
        model: type[M] | None = None
    ) -> None:
        '''
        Accepts an AsyncSession and an optional model class, if not provided
        as a class variable.

        Parameters
        ----------
        db : AsyncSession
        model : type[M] | None, optional
            _The model to use if not defined in class_, by default None

        Raises
        ------
        ValueError
            _If no model is provided as a parameter or defined in class_
        '''
        self.db: AsyncSession = db
        if not model and not hasattr(self, 'model'):
            raise ValueError(
                'You must provide a model or set the model attribute.'
            )
        elif model:
            self.model = model

        self.logger = logging.getLogger(__name__)

    @property
    def tablename(self) -> str:
        return self.model.__tablename__  # type: ignore

    async def save(self, *, commit: bool = True) -> None:
        '''
        Commits the current transaction if commit is True.

        Parameters
        ----------
        commit : bool, optional
            Whether to commit the transaction, by default True
        '''
        await sql_cmds.try_save_db(
            self.db,
            table_name=self.tablename,
            commit=commit,
            flush=not commit,
        )


    async def first_row(self, statement: Select) -> dict | None:
        '''`mappings().first()` and then casted to dict()'''
        result = await self.db.execute(statement)
        mapping = result.mappings().first()
        return dict(mapping) if mapping else None

    async def list_rows(self, statement: Select) -> list[dict]:
        '''`mappings().all()` and then casted to list[dict()]'''
        result = await self.db.execute(statement)
        return [dict(row) for row in result.mappings().all()] or []

    async def first_orm(self, statement: Select) -> M | None:
        '''`scalar().first()`'''
        result = await self.db.execute(statement)
        return result.scalar()

    async def list_orms(self, statement: Select) -> list[M]:
        '''`scalars().all()`'''
        result = await self.db.execute(statement)
        models = result.scalars().all()
        return list(models) if models else []

    async def one_orm(self, statement: Select) -> M | None:
        '''`scalars().one_or_none()`'''
        result = await self.db.execute(statement)
        return result.scalars().one_or_none()

    async def create(self, **kwargs) -> M:
        '''
        Creates a new model instance with the given kwargs,
        adds it to the session and commits.

        Parameters
        ----------
        **kwargs : dict
            The fields to set on the new model instance.

        Returns
        -------
        M
            The created model instance.
        '''
        instance = self.model(**kwargs)  # type: ignore
        self.db.add(instance)
        await sql_cmds.try_save_db(self.db, self.tablename)
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: M, **kwargs) -> bool:
        '''
        Updates the given model instance with the provided kwargs,
        adds it to the session and commits.

        Parameters
        ----------
        instance : M
            The model instance to update.
        **kwargs : dict
            The fields to update on the model instance.

        Returns
        -------
        M
            The updated model instance.
        '''
        try:
            sql_cmds.patch_db_model(instance, **kwargs)
        except Exception as e:
            self.logger.error(f'Error updating {self.tablename} - {e}')
            return False

        self.db.add(instance)
        await sql_cmds.try_save_db(self.db, self.tablename)
        await self.db.refresh(instance)
        return True

    async def delete(self, instance: M) -> None:
        '''
        Deletes the given model instance from the session and commits.

        Parameters
        ----------
        instance : M
            The model instance to delete.
        '''
        await self.db.delete(instance)
        await sql_cmds.try_save_db(self.db, self.tablename)

    async def stream_dicts(self, statement: Select) -> AsyncGenerator[dict, None]:
        '''
        Streams the results of the given select statement as dictionaries.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        dict
        '''
        stream = await self.db.stream(statement)
        async for row in stream.mappings():
            yield dict(row)

    async def stream_orms(self, statement: Select) -> AsyncGenerator[M, None]:
        '''
        Streams the results of the given select statement as model instances.

        Parameters
        ----------
        statement : Select

        Yields
        ------
        M
        '''
        stream = await self.db.stream(statement)
        async for row in stream.scalars():
            yield row

    async def count_rows(self, statement: Select) -> int:
        '''
        Counts the number of rows that would be returned by the given
        select statement.

        Parameters
        ----------
        statement : Select

        Returns
        -------
        int
        '''
        stmnt = select(func.count()).select_from(statement.subquery())
        result = await self.db.execute(stmnt)
        return result.scalar_one() or 0