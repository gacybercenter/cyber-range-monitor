'''
A generic SQL repository using SQLAlchemy async sessions
with utility functions for executing select statements

Raises
------
ValueError
    If no model is provided as a parameter or defined in class
'''

import logging
import uuid
from collections.abc import AsyncGenerator, Sequence
from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import Result, Select, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.interfaces import ORMOption

from server.db import sql_cmds

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SQLRepository[M: DeclarativeBase | Any]:
    model: type[M]
    db: AsyncSession

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

    def select(self) -> Select:
        '''
        Creates a basic select statement for the repository's model.

        Returns
        -------
        Select
        '''
        return select(self.model)

    async def read(
        self,
        entity_id: uuid.UUID | int | str,
        *,
        with_for_update: bool = False,
        options: Sequence[ORMOption] | None = None,
    ) -> M | None:
        return await self.db.get(
            self.model,
            entity_id,
            with_for_update=with_for_update,
            options=options,
        )

    async def get_row(self, select_stmt: Select) -> dict | None:
        '''`mappings().first()` and then casted to dict()'''
        result = await self.db.execute(select_stmt)
        mapping = result.mappings().first()
        return dict(mapping) if mapping else None

    async def list_rows(self, select_stmt: Select) -> list[dict]:
        '''`mappings().all()` and then casted to list[dict()]'''
        result = await self.db.execute(select_stmt)
        return [dict(row) for row in result.mappings().all()] or []

    async def get_model(self, select_stmt: Select) -> M | None:
        '''`scalar().first()`'''
        result = await self.db.execute(select_stmt)
        return result.scalar()

    async def list_models(self, select_stmt: Select) -> list[M]:
        '''`scalars().all()`'''
        result = await self.db.execute(select_stmt)
        models = result.scalars().all()
        return list(models) if models else []

    async def insert(self, **kwargs) -> M:
        stmnt = insert(self.model).values(**kwargs).returning(self.model)
        result = await self.db.execute(stmnt)
        return result.scalar_one()

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
            sql_cmds.set_model_attrs(instance, **kwargs)
        except Exception as e:
            logger.error(f'Error updating {self.tablename} - {e}')
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

    async def count(self, *where) -> int:
        '''
        Counts the number of rows that would be returned by the given
        select statement.

        Parameters
        ----------
        *where : Any
            The SQLAlchemy where clauses.

        Returns
        -------
        int
        '''
        stmnt = select(func.count()).select_from(self.model)
        if where:
            stmnt = stmnt.where(*where)

        result = await self.db.execute(stmnt)
        return result.scalar_one() or 0

    async def stream_rows(self, statement: Select) -> AsyncGenerator[dict]:
        '''
        Streams the results of the given select statement as dictionaries.

        Parameters
        ----------
        statement : Select
            The SQLAlchemy select statement.

        Yields
        ------
        dict
        '''
        stream = await self.db.stream(statement)
        async for row in stream.mappings():
            yield dict(row)

    async def stream_models(self, statement: Select) -> AsyncGenerator[M]:
        '''
        Streams the results of the given select statement as model instances.
        '''
        stream = await self.db.stream(statement)
        async for row in stream.scalars():
            yield row

    async def exec(
        self,
        operation: str,
        statement: Any,
        *,
        commit: bool = False
    ) -> Result:
        '''
        Executes the given SQLAlchemy statement.

        Parameters
        ----------
        statement : Any
            The SQLAlchemy statement to execute.
        operation : str
            A string describing the operation for logging purposes.
        commit : bool, optional
            Whether to commit the transaction after execution, by default False

        Returns
        -------
        Any
        '''
        async with sql_cmds.catch_db_failure(
            self.db,
            self.tablename,
            operation
        ):
            result = await self.db.execute(statement)
            if commit:
                await self.db.commit()
            return result


def redis_key(*parts: str) -> str:
    return ':'.join(parts)


class RedisRepository:
    '''
    simple wrapper around a Redis client to be used as a repository
    which will likely be extended in the future with common methods
    '''

    def __init__(self, redis: Redis) -> None:
        self.redis: Redis = redis
