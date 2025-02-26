from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession
)

from app.configs.database import DatabaseConfig
from .const import DATABASE_CONFIG


engine = create_async_engine(
    url=DATABASE_CONFIG.URL,
    echo=DATABASE_CONFIG.ECHO,
    connect_args=DATABASE_CONFIG.connect_args()
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def connect_db() -> None:
    '''creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    '''    
    url_dir = DATABASE_CONFIG.resolve_url_dir()
    if not os.path.exists(url_dir):
        os.mkdir(url_dir)
    async with engine.begin() as conn:
        from app.models.base import Base
        await conn.run_sync(Base.metadata.create_all)  

    
    
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
    async with engine.begin() as conn:
        for pragma, value in DATABASE_CONFIG.pragmas().items():
            await conn.execute(text(f'PRAGMA {pragma}={value}'))
    
    
    

