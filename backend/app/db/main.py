import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import settings

db_config = settings.get_config_yml().database

engine = create_async_engine(
    url=db_config.url,
    echo=db_config.sqlalchemy_echo,
    connect_args=db_config.connect_args(),
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def connect_db() -> None:
    """creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    """
    url_dir = db_config.resolve_url_dir()
    if not os.path.exists(url_dir):
        os.mkdir(url_dir)
    async with engine.begin() as conn:
        from app.models.base import Base

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


async def set_db_pragmas() -> None:
    async with engine.begin() as conn:
        db_pragmas = db_config.pragmas()
        for pragma, value in db_pragmas.items():
            await conn.execute(text(f"PRAGMA {pragma}={value}"))
