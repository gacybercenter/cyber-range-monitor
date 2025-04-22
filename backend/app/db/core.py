import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine
)

from app import config

from .const import ENGINE_OPTIONS
from .models.base import DatabaseModel

yml_config = config.get_config_yml()
db_config = yml_config.database

def _create_engine() -> AsyncEngine:
    if yml_config.app.testing:
        return create_async_engine(
            url=db_config.url,
            echo=db_config.sqlalchemy_echo,
            connect_args=db_config.connect_args(),
        )
    return create_async_engine(
        url=db_config.url,
        echo=db_config.sqlalchemy_echo,
        **ENGINE_OPTIONS.model_dump(),
        connect_args=db_config.connect_args()
    )



engine = _create_engine()

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def setup_db_file() -> None:
    url_dir = db_config.url_dirname()
    if not os.path.exists(url_dir):
        os.mkdir(url_dir)


def check_and_handle_setup() -> bool:
    url_dir = db_config.url_dirname()
    first_run = not os.path.exists(url_dir)
    if first_run:
        os.mkdir(url_dir)
    return first_run
    
async def connect_db() -> None:
    """creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    """
    first_run = check_and_handle_setup()
    
    async with engine.begin() as conn:
        from . import models  # noqa: F401 (without this line, sqlalchemy doesn't know about the models)
        await conn.run_sync(DatabaseModel.metadata.create_all)
        db_pragmas = db_config.get_pragmas()
        for pragma, value in db_pragmas.items():
            await conn.execute(text(f'PRAGMA {pragma}={value}'))

    if first_run and not yml_config.app.testing:
        from . import seed
        await seed.default_seed()

    logging.getLogger('sqlalchemy').setLevel(
        yml_config.logging.db_level
    )


async def get_db() -> AsyncSession:  # type: ignore
    """yields a single async session, this is the dependency version
    if you need the db seperate from a request use get_session()
    context manager.

    Returns:
        AsyncSession -- the session
    """
    async with AsyncSessionLocal() as session:
        yield session  # type: ignore


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """used in instances where db is needed outside of a dependency hence the context manager"""
    async with AsyncSessionLocal() as session:
        yield session
