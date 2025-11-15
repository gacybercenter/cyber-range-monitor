from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Final

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from server.settings import get_app_settings, get_secret_settings

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncEngine

    from server.configs.secrets import SecretSettings
    from server.configs.toml import SqlalchemyConfig


logger = logging.getLogger(__name__)


_SQLITE_PRAGMAS: Final[list[str]] = [
    'foreign_keys=ON',
    'journal_mode=WAL',
    'synchronous=NORMAL',
    'cache_size=-64000',
    'temp_store=MEMORY',
    'busy_timeout=10000',
    'wal_autocheckpoint=1000',
]


def get_async_engine(
    *,
    orm_options: SqlalchemyConfig | None = None,
    secrets: SecretSettings | None = None,
) -> AsyncEngine:
    orm_options = orm_options or get_app_settings().sql_alchemy
    secrets = secrets or get_secret_settings()
    engine = create_async_engine(
        secrets.get_sqlite_url(sync=False),
        echo=orm_options.echo,
        future=True,
        pool_size=orm_options.pool_size,
        max_overflow=orm_options.max_overflow,
        pool_recycle=orm_options.pool_recycle,
        pool_pre_ping=orm_options.pool_pre_ping,
        connect_args={
            'check_same_thread': False,
            'timeout': orm_options.timeout,
        },
    )

    @sa.event.listens_for(engine.sync_engine, 'connect')
    def _register_pragmas(dbapi_conn, connection_record) -> None:  # noqa: ANN001
        logger.info('Setting SQLite pragmas on new connection...')
        cursor = dbapi_conn.cursor()
        pragmas = _SQLITE_PRAGMAS
        for pragma in pragmas:
            cursor.execute(f'PRAGMA {pragma};')
        cursor.close()

    return engine


def get_async_sessionmaker(
    engine: AsyncEngine,
    *,
    orm_options: SqlalchemyConfig | None = None,
) -> async_sessionmaker[AsyncSession]:
    orm_options = orm_options or get_app_settings().sql_alchemy
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=orm_options.expire_on_commit,
        autoflush=orm_options.autoflush,
        class_=AsyncSession,
    )


async_engine = get_async_engine()
AsyncSessionLocal = get_async_sessionmaker(async_engine)


@contextlib.asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@contextlib.asynccontextmanager
async def get_transaction() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()


async def dispose_db() -> None:
    '''
    Disposes of the database engine, closing all connections.

    Returns
    -------
    None
    '''
    logger.info('Disposing database engine...')
    await async_engine.dispose()


async def is_db_reachable() -> bool:
    '''
    Pings the SQLite database to ensure connectivity.

    Returns
    -------
    bool
        True if the ping was successful, False otherwise.
    '''
    logger.info('Pinging database...')
    try:
        async with async_engine.connect() as conn:
            await conn.execute(sa.text('SELECT 1'))
    except Exception:
        return False

    return True


async def create_tables() -> None:
    logger.info('Creating database tables...')
    async with async_engine.begin() as conn:
        from server.models import MappedBase

        await conn.run_sync(MappedBase.metadata.create_all)
    logger.info('Database tables created.')


async def drop_tables() -> None:
    logger.info('Dropping database tables...')
    async with async_engine.begin() as conn:
        from server.models import MappedBase

        await conn.run_sync(MappedBase.metadata.drop_all)
    logger.info('Database tables dropped.')
