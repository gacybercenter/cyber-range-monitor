from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os
from api.config import settings
from .defaults import insert_table_defaults


_PRAGMAS: dict = {
    "journal_mode": "WAL",
    "foreign_keys": "ON",
    "busy_timeout": 5000
}

_CONNECT_ARGS: dict = {
    "check_same_thread": False,
    "timeout": 30,
}

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args=_CONNECT_ARGS,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


async def init_db() -> None:
    '''
    creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    '''
    if settings.DATABASE_USE_PRAGMAS:
        await set_db_pragmas()

    async with engine.begin() as conn:
        from api.models.base import Base
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:  # type: ignore
    '''yields a single async session'''
    async with SessionLocal() as session:
        yield session  # type: ignore


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    '''
        used in instances where db is needed outside of a dependency
    '''
    async with SessionLocal() as session:
        yield session


async def seed_db() -> None:
    '''seeds the database with default values'''
    if not os.path.exists('instance'):
        raise FileNotFoundError(
            'The instance directory does not exist, please create it before seeding the database')

    async with SessionLocal() as session:
        await insert_table_defaults(session)


async def set_db_pragmas() -> None:
    global engine, _PRAGMAS
    async with engine.begin() as conn:
        for pragma, value in _PRAGMAS.items():
            await conn.execute(text(f'PRAGMA {pragma} = {value}'))
