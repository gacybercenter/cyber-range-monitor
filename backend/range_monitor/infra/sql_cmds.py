'''
A generic SQL utility functions for streaming executed statements,
getting results, and common CRUD operations.

Raises
------
ValueError
    If no model is provided as a parameter or defined in class

DatabaseFailure
    If a database operation fails, (i.e) `save()` fails
    handle in error handler by returning a 500 error to the client
    this will almost never occur and is just a failsafe mechanism
'''

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from range_monitor.core.errors import DatabaseFailure

M = TypeVar('M', bound=DeclarativeBase | Any)
logger = logging.getLogger(__name__)


async def stream_sql_rows(
    query: Select,
    db: AsyncSession,
    unique: bool = False
) -> AsyncGenerator[dict, None]:
    '''
    Streams rows from the executed statement as dictionaries.

    Parameters
    ----------
    query : Select
        _The SQLAlchemy select statement to execute_
    db : AsyncSession
        _The async database session_

    Yields
    ------
    Iterator[AsyncGenerator[dict, None]]
        The result rows as dictionaries, `dict(row.mappings())`
    '''
    async with db.stream(query) as result:
        if unique:
            result = result.unique()
        async for mapping in result.mappings():
            yield dict(mapping)


async def stream_db_models(
    query: Select,
    db: AsyncSession,
    unique: bool = False
):
    '''
    Streams ORM instances from the executed statement.

    Parameters
    ----------
    query : Select
        _The SQLAlchemy select statement to execute_
    db : AsyncSession
        _The async database session_
    Yields
    ------
    Iterator[AsyncGenerator[M, None]]
        The result rows as ORM instances, `row.scalar()`
    '''
    async with db.stream(query) as result:
        if unique:
            result = result.unique()
        async for scalar in result.scalars():
            yield scalar


def esc_like(val: str) -> str:
    '''
    Sanitizes a string for use in a SQL LIKE query by escaping

    Parameters
    ----------
    val : str

    Returns
    -------
    str
    '''
    return val.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def create_model(db: AsyncSession, model: type[M], **kwargs) -> M:
    '''
    Creates and returns a new model instance and adds it to the session.
    does NOT commit or flush.

    Parameters
    ----------
    db : AsyncSession
    model : type[M]
    **kwargs : Any
        _The attributes to set on the model_

    Returns
    -------
    M
    '''
    instance = model(**kwargs)
    db.add(instance)
    logger.info(f'Created new {model.__tablename__} instance.')
    return instance


def patch_db_model(model: Any, **kwargs) -> None:
    '''
    does best effort attempt to set attributes on the model

    Parameters
    ----------
    model : Any
        The ORM model instance
    **kwargs : Any
        The attributes to set on the model
    '''
    logger.info(f'Patching model {model}...')
    try:
        for key, value in kwargs.items():
            setattr(model, key, value)
    except Exception as e:
        model_id = getattr(model, 'id', None) or 'unknown'
        logging.getLogger(__name__).error(
            f'Error setting attributes on {model.__class__.__name__} '
            f'instance {model_id}',
            exc_info=e
        )
        raise


@asynccontextmanager
async def catch_db_failure(db: AsyncSession, table_name: str, operation: str):
    '''
    Context manager to catch database operation failures and
    raise a DatabaseFailure exception.

    Parameters
    ----------
    db : AsyncSession
    table_name : str
    operation : str

    Raises
    ------
    DatabaseFailure
    '''
    try:
        yield
    except Exception as e:
        await db.rollback()
        logger.error(
            f'Database operation failure on {table_name} during {operation}: {e}',
            exc_info=e
        )
        raise DatabaseFailure(
            table_name=table_name,
            operation=operation,
            orig_exc=e
        )


async def try_save_db(
    db: AsyncSession,
    table_name: str,
    *,
    commit: bool = True,
    flush: bool = False
) -> None:
    '''
    Saves changes to the database session.

    Parameters
    ----------
    db : AsyncSession
    table_name : str
    commit : bool, optional
        _Whether to commit the transaction_, by default True
    flush : bool, optional
        _Whether to flush the session_, by default False

    Raises
    ------
    ValueError
        If both commit and flush are True
    '''
    if commit and flush:
        raise ValueError('Cannot commit and flush at the same time.')

    operation = f'save_{table_name}_and_{"flush" if flush else "commit"}'
    async with catch_db_failure(db, table_name, operation):

        if flush:
            await db.flush()

        if commit:
            await db.commit()


async def count_selected_rows(
    db: AsyncSession,
    model: type[M],
    statement: Select
) -> int:
    '''
    Counts the total number of records that would be returned

    Parameters
    ----------
    db : AsyncSession
    model : type[M]
    statement : Select

    Returns
    -------
    int
    '''
    total_stmnt = select(func.count()).select_from(model)
    if whereclause := statement._whereclause:  # type: ignore
        total_stmnt = total_stmnt.where(whereclause)

    total = await db.execute(total_stmnt)
    return total.scalar_one_or_none() or 0

