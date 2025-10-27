import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, TypeVar

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

M = TypeVar('M', bound=DeclarativeBase | Any)
logger = logging.getLogger(__name__)


async def stream_sql_rows(
    query: Select, db: AsyncSession, *, unique: bool = False
) -> AsyncGenerator[dict]:
    '''
    Streams rows from the executed statement as dictionaries.
    '''
    async with db.stream(query) as result:
        if unique:
            result = result.unique()
        async for mapping in result.mappings():
            yield dict(mapping)


async def stream_db_models(query: Select, db: AsyncSession, *, unique: bool = False):  # noqa: ANN201
    '''
    Streams ORM instances from the executed statement returing the result rows
    as ORM instances, `row.scalar()`
    '''
    async with db.stream(query) as result:
        if unique:
            result = result.unique()
        async for scalar in result.scalars():
            yield scalar


def sanitize_like(val: str) -> str:
    '''
    Sanitizes a string for use in a SQL LIKE query by escaping
    '''
    return val.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def set_model_attrs(model: Any, **kwargs) -> None:
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
            f'Error setting attributes on {model.__class__.__name__} instance {model_id}',
            exc_info=e,
        )
        raise


@asynccontextmanager
async def catch_db_failure(
    db: AsyncSession, table_name: str, operation: str
) -> AsyncGenerator[None]:
    """
    Context manager to catch database operation failures and
    raise a DatabaseFailure exception.

    Parameters
    ----------
    db : AsyncSession
        The async database session
    table_name : str
        The name of the table being operated on
    operation : str
        The operation being performed (e.g., 'save', 'update')

    Raises
    ------
    DatabaseFailure
    """
    try:
        yield
    except Exception as e:
        await db.rollback()
        logger.error(
            f'Database operation failure on {table_name} during {operation}: {e}',
            exc_info=e,
        )
        raise


async def try_save_db(
    db: AsyncSession, table_name: str, *, commit: bool = True, flush: bool = False
) -> None:
    '''
    Saves changes to the database session.

    Parameters
    ----------
    db : AsyncSession
        The async database session
    table_name : str
        _The name of the table being operated on_
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
