import contextlib
import logging
import time
from collections.abc import AsyncGenerator, Generator
from typing import Any

import aiosqlite
from sqlalchemy import URL, func, select, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db_model import MappedBase
from app.utils import path_utils

from . import const
from .settings import db_secrets, sqlalchemy_options

logger = logging.getLogger(__name__)


def _create_engine(
    *,
    drivername: str = const.DB_DRIVER_NAME,
    database: str = db_secrets.database,
    echo: bool = db_secrets.ECHO,
    connect_args: dict[str, Any] = const.CONNECT_ARGS,
    engine_kwargs: dict[str, Any] = sqlalchemy_options.engine_kwargs,
) -> AsyncEngine:
    db_url = URL.create(drivername=drivername, database=database)
    logger.debug(f"Connecting to database URL: {db_url}")
    return create_async_engine(
        url=db_url,
        echo=echo,
        connect_args=connect_args,
        **engine_kwargs,
    )


def _create_async_session_maker(
    engine: AsyncEngine,
    *,
    expire_on_commit: bool = sqlalchemy_options.expire_on_commit,
    autoflush: bool = sqlalchemy_options.autoflush,
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=expire_on_commit,
        autoflush=autoflush,
        class_=AsyncSession,
    )


_async_engine = _create_engine()
_AsyncSessionLocal = _create_async_session_maker(_async_engine)


async def _set_sqlite_pragmas(conn: AsyncConnection) -> None:
    for pragma, value in const.PRAGMAS.items():
        prgama_stmnt = text(f"PRAGMA {pragma} = {value}")
        await conn.execute(prgama_stmnt)
    logger.info("SQLite PRAGMAs set successfully.")


async def connect_db(
    *,
    run_seed: bool = sqlalchemy_options.run_seed,
) -> None:
    """connects to the database and creates the tables if they do not exist"""
    if db_secrets.FILE_NAME != ":memory:":
        root = path_utils.get_app_root()
        db_path = root.joinpath(db_secrets.DIRECTORY)
        db_path.mkdir(exist_ok=True)

    logger.info("Connecting to the database...")
    async with _async_engine.begin() as conn:
        from . import _mapped_models  # noqa: F401

        await _set_sqlite_pragmas(conn)
        logger.info("Creating database tables if they do not exist...")
        await conn.run_sync(MappedBase.metadata.create_all)

    if run_seed:
        logger.info("Seeding database...")
        await seed_db()

    logger.info("Database setup complete.")


async def disconnect_db() -> None:
    """disconnects from the database"""
    await _async_engine.dispose()
    logger.info("Database connection closed.")


@contextlib.asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a database session to the caller within a context manager

    Returns
    -------
    AsyncSession

    Yields
    ------
    Iterator[AsyncSession]
    """
    async with _AsyncSessionLocal() as session:
        yield session  # type: ignore


async def seed_db() -> None:
    """Seeds the database with initial data."""
    from .seed import get_seed_data

    data = get_seed_data()
    async with _AsyncSessionLocal() as session:
        for seeds in data:
            session.add_all(seeds)
        await session.commit()
    logger.info("Database seeded successfully.")


async def get_model_metadata(model: Any, db: AsyncSession) -> dict:
    """Returns general database about a model in the database.

    Args:
        model (Any): _the database model_
        db (AsyncSession): _the session to use_

    Returns:
        dict: _model meta data_
    """
    table_name = model.__tablename__
    read_start = time.perf_counter()
    statement = select(func.count()).select_from(model)  # type: ignore
    result = await db.execute(statement)
    row_count = result.scalar_one()
    read_time = time.perf_counter() - read_start
    return {"table_name": table_name, "row_count": row_count, "read_time": read_time}


async def get_server_version(db: AsyncSession) -> Any:
    """Returns the server version of the database."""
    result = await db.execute(text("SELECT sqlite_version()"))
    return result.scalar()


def iter_db_models() -> Generator[Any, None, None]:
    """Returns an iterator over the database models."""
    from ._mapped_models import MODEL_LIST

    for model in MODEL_LIST:
        yield model


async def get_database_info(db: AsyncSession) -> dict:
    """Returns the database information."""
    from ._mapped_models import MODEL_LIST

    model_data = [await get_model_metadata(model, db) for model in MODEL_LIST]
    server_version = await get_server_version(db)
    return {
        "server_version": server_version,
        "driver": f"{db_secrets.DRIVER_NAME} {aiosqlite.__version__}",
        "table_meta": model_data,
    }
