from contextlib import asynccontextmanager
import os
from typing import AsyncGenerator
from sqlalchemy import text, event
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession
)
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

@event.listens_for(engine.sync_engine, 'connect')
def set_sqlite_pragmas(dbapi_connection, connection_record) -> None:
    '''sets the pragmas for the SQLite database'''
    pragmas = DATABASE_CONFIG.pragmas()
    for pragma, value in pragmas.items():
        dbapi_connection.execute(f'PRAGMA {pragma} = {value}')
    dbapi_connection.close()
    
async def connect_db() -> None:
    '''creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    '''
    
    url_dir = DATABASE_CONFIG.resolve_url_dir()
    if not os.path.exists(url_dir):
        os.makedirs(url_dir)
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
