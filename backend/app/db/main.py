
import os
import logging
import time
import aiosqlite

from typing import Any
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)
from app.common.models import MappedBase
from sqlalchemy import URL, select, func, text


from .config import db_settings
from .const import CONNECT_ARGS, DB_DRIVER_NAME, PRAGMAS

logger = logging.getLogger(__name__)


def create_engine() -> AsyncEngine:
    """Creates an async SQLAlchemy engine for the ORM plugin."""
    db_url = URL.create(
        drivername=DB_DRIVER_NAME,
        database=db_settings.database()
    )
    return create_async_engine(
        url=db_url,
        echo=db_settings.echo,
        connect_args=CONNECT_ARGS,
        **db_settings.engine.model_dump()
    )


async_engine = create_engine()
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False
)


async def connect_database() -> None:
    '''connects to the database and creates the tables if they do not exist'''
    first_run = False
    if db_settings.file_name != ":memory:":
        os.makedirs(db_settings.directory, exist_ok=True)

    async with async_engine.begin() as conn:
        from . import models  # noqa: F401
        await conn.run_sync(MappedBase.metadata.create_all)
        for k, v in PRAGMAS.items():
            await conn.execute(text(f"PRAGMA {k} = {v}"))

    if db_settings.run_seed:
        logger.info("Seeding database...")
        await seed_db()

    logger.info("Database setup complete.")


async def disconnect_database() -> None:
    '''disconnects from the database'''
    await async_engine.dispose()
    logger.info("Database connection closed.")


async def get_session() -> AsyncSession:  # type: ignore
    '''Yields an async database session.

    Returns:
        AsyncGenerator[AsyncSession, None]: async session

    Yields:
        Iterator[AsyncGenerator[AsyncSession, None]]: async session
    '''
    async with AsyncSessionLocal() as session:
        yield session  # type: ignore


async def seed_db() -> None:
    '''Seeds the database with initial data.'''
    from .seed import get_seed_data
    data = get_seed_data()
    async with AsyncSessionLocal() as session:
        for seeds in data:
            session.add_all(seeds)
        await session.commit()
    logger.info("Database seeded successfully.")


async def get_model_metadata(model: Any, db: AsyncSession) -> dict:
    '''Returns general database about a model in the database.

    Args:
        model (Any): _the database model_
        db (AsyncSession): _the session to use_

    Returns:
        dict: _model meta data_
    '''
    table_name = model.__tablename__
    read_start = time.perf_counter()
    statement = select(func.count()).select_from(model)  # type: ignore
    result = await db.execute(statement)
    row_count = result.scalar_one()
    read_time = time.perf_counter() - read_start
    return {
        'table_name': table_name,
        'row_count': row_count,
        'read_time': read_time
    }


async def get_server_version(db: AsyncSession) -> Any:
    """Returns the server version of the database."""
    result = await db.execute(text("SELECT sqlite_version()"))
    return result.scalar()


async def get_database_info(db: AsyncSession) -> dict:
    """Returns the database information."""
    from .models import MODEL_LIST
    model_data = [
        await get_model_metadata(model, db)
        for model in MODEL_LIST
    ]
    server_version = await get_server_version(db)
    return {
        'server_version': server_version,
        'driver': f'{DB_DRIVER_NAME} {aiosqlite.__version__}',
        'table_meta': model_data
    }
