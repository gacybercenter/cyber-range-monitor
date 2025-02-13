from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import running_config

_PRAGMAS: dict = {
    "journal_mode": "WAL",
    "foreign_keys": "ON",
    "busy_timeout": 5000
}

_CONNECT_ARGS: dict = {
    "check_same_thread": False,
    "timeout": 30,
}

settings = running_config()

engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args=_CONNECT_ARGS,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)


def parse_db_path(db_url: str) -> str:
    '''
    extracts the path from a database url
    '''
    return db_url.split('///')[1]


async def connect_db() -> None:
    '''
    creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    '''
    db_path = parse_db_path(settings.DATABASE_URL)
    db_dir = os.path.dirname(db_path)
    is_first_run = not os.path.exists(db_dir)
    
    if is_first_run:
        os.makedirs(db_dir)
        
    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)

    if is_first_run:
        from scripts.seed_db import main
        await main()



async def get_db() -> AsyncSession:  # type: ignore
    '''yields a single async session, this is the dependency version 
    if you need the db seperate from a request use get_session()
    context manager.
    
    Returns:
        AsyncSession -- the session
    '''
    async with AsyncSessionLocal() as session:
        yield session  # type: ignore


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    '''used in instances where db is needed outside of a dependency'''
    async with AsyncSessionLocal() as session:
        yield session


async def set_db_pragmas() -> None:
    global engine, _PRAGMAS
    async with engine.begin() as conn:
        for pragma, value in _PRAGMAS.items():
            await conn.execute(text(f'PRAGMA {pragma} = {value}'))
