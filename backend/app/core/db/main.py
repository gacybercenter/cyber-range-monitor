import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import config

from app.extensions import api_console

db_config = config.get_database_config()

engine = create_async_engine(
    url=db_config.url,
    echo=db_config.sqlalchemy_echo,
    # future=True,
    connect_args=db_config.connect_args(),
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


def setup_db() -> None:
    url_dir = db_config.resolve_url_dir()
    if not os.path.exists(url_dir):
        os.mkdir(url_dir)

async def connect_db() -> None:
    """creates / initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    """
    is_testing = config.get_app_config().testing
    if not is_testing:
        setup_db()
    await set_db_pragmas()
    async with engine.begin() as conn:
        from app.core.models import Base
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
            pragma_str = f"PRAGMA {pragma}={value}"
            api_console.debug(f'Setting Pragma: {pragma_str}')
            await conn.execute(text(pragma_str))
