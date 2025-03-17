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

from app.extensions import api_console

from .const import ENGINE_OPTIONS, Base

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
        connect_args=db_config.connect_args(),
    )
    
    
    

engine = _create_engine() 

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def setup_db_file() -> None:
    url_dir = db_config.url_dirname()
    if not os.path.exists(url_dir):
        os.mkdir(url_dir)


async def connect_db() -> None:
    """creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    """
    if not yml_config.app.testing:
        setup_db_file()
    async with engine.begin() as conn:
        db_pragmas = db_config.get_pragmas()
        for pragma, value in db_pragmas.items():
            api_console.debug(f'Setting Pragma: {pragma}={value}')
            await conn.execute(text(f'PRAGMA {pragma}={value}'))
        await conn.run_sync(Base.metadata.create_all)


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
    """used in instances where db is needed outside of a dependency"""
    async with AsyncSessionLocal() as session:
        yield session
