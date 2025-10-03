from __future__ import annotations

import dataclasses as dc
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Self

from sqlalchemy import URL, event, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from range_monitor.core import constant
from range_monitor.infra.db import seed
from range_monitor.infra.db.base import MappedModel
from range_monitor.infra.db.config import SqliteConfig
from range_monitor.infra.security import CryptoPolicy

logger = logging.getLogger(__name__)

def create_url(*, is_testing: bool = False) -> URL:
    if is_testing:
        return URL.create(
            drivername=constant.DATABASE_DRIVERNAME,
            database=':memory:',
            query={
                'mode': 'memory',
                'cache': 'shared',
                'uri': 'true',
            }
        )

    db = f'{constant.DATABASE_DIR_PATH}/{constant.DATABASE_FILENAME}'

    return URL.create(
        drivername=constant.DATABASE_DRIVERNAME,
        database=os.fspath(db),
    )

def _add_sqlite_pragmas(dbapi_conn, pragmas: list[str]) -> None:
    if not pragmas:
        return

    cursor = dbapi_conn.cursor()
    for pragma in pragmas:
        cursor.execute(f'PRAGMA {pragma};')
    cursor.close()


async def _register_models(conn: AsyncConnection) -> None:
    from range_monitor.sources.models import (  # noqa: F401
        Guacamole,
        Openstack,
        Saltstack,
    )
    from range_monitor.users.models import User  # noqa: F401
    await conn.run_sync(MappedModel.metadata.create_all)

def get_db_path() -> Path:
    '''
    Returns the path to the SQLite database file.
    '''
    return Path(constant.DATABASE_DIR_PATH, constant.DATABASE_FILENAME)


@dc.dataclass(slots=True)
class SqliteDatabase:
    '''
    An instance for managing the connection to the SQLite database.
    '''
    options: SqliteConfig
    url: URL
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]


    async def create_tables(self, crypto_policy: 'CryptoPolicy') -> None:
        logger.info('Creating tables for database.')
        should_seed = not get_db_path().exists()

        async with self.engine.begin() as conn:
            await _register_models(conn)

        if should_seed:
            await self.seed_tables(crypto_policy)

        logger.info('Tables created successfully.')

    async def drop_tables(self) -> None:
        logger.info('Dropping all tables in SQLite database.')
        async with self.engine.begin() as conn:
            await conn.run_sync(MappedModel.metadata.drop_all)
        logger.info('All tables dropped successfully.')

    async def disconnect(self) -> None:
        logger.info('Disconnecting from SQLite database.')
        await self.engine.dispose()

    @asynccontextmanager
    async def session(self):
        '''
        Creates a new SQLAlchemy AsyncSession.

        Returns
        -------
        AsyncSession
        '''
        logger.info('Creating new database session...')
        async with self.sessionmaker() as session:
            yield session

    @asynccontextmanager
    async def readonly_session(self):
        logger.info('Creating new readonly database session...')
        async with self.sessionmaker() as session:
            session.autoflush = False
            await session.execute(text('BEGIN;'))
            await session.execute(text('PRAGMA query_only = TRUE;'))
            try:
                yield session
            finally:
                await session.rollback()

    async def seed_tables(self, crypto_service: 'CryptoPolicy') -> None:
        from range_monitor.infra.security import CryptoService
        logger.info('Seeding the database with initial data...')

        service = CryptoService(policy=crypto_service)

        async with self.session() as session:
            await seed.insert_seed_data(
                db=session,
                crypto_service=service
            )

        logger.info('Database seeding complete.')

    @classmethod
    def from_config(
        cls,
        config: SqliteConfig,
        *,
        is_testing: bool = False
    ) -> Self:
        url = create_url(is_testing=is_testing)
        engine = create_async_engine(url, **config.engine_kwargs)

        @event.listens_for(engine.sync_engine, 'connect')
        def _set_sqlite_pragmas(dbapi_conn, connection_record):
            _add_sqlite_pragmas(dbapi_conn, config.pragmas)

        sessionmaker = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            autoflush=config.autoflush,
            expire_on_commit=config.expire_on_commit,
        )

        return cls(
            options=config,
            url=url,
            engine=engine,
            sessionmaker=sessionmaker
        )
