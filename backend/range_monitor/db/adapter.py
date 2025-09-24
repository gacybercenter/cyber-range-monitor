

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Self

from sqlalchemy import URL, event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from range_monitor.core import constant
from range_monitor.db.base import MappedModel
from range_monitor.lifespan import dataclass

if TYPE_CHECKING:
    from range_monitor.db.config import SqliteOptions

logger = logging.getLogger(__name__)

def create_url(
    *,
    is_testing: bool = False,
) -> URL:
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

def add_sqlite_pragmas(dbapi_conn, pragmas: list[str]) -> None:
    if not pragmas:
        return

    cursor = dbapi_conn.cursor()
    for pragma in pragmas:
        cursor.execute(f'PRAGMA {pragma};')
    cursor.close()


@dataclass(slots=True)
class SqliteDatabase:
    '''
    An instance for managing the connection to the SQLite database.
    '''
    options: 'SqliteOptions'
    url: URL
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]


    async def create_tables(self) -> None:
        logger.info('Creating tables for database.')
        async with self.engine.begin() as conn:
            await conn.run_sync(MappedModel.metadata.create_all)
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
        async with self.sessionmaker() as session:
            yield session

    @asynccontextmanager
    async def readonly_session(self):
        async with self.sessionmaker() as session:
            session.autoflush = False
            await session.execute(text('BEGIN;'))
            await session.execute(text('PRAGMA query_only = TRUE;'))
            try:
                yield session
            finally:
                await session.rollback()

    def run_migrations(
        self,
        *,
        alembic_ini_path: str = 'alembic.ini',
        revisions: str = 'head'
    ) -> None:
        config = AlembicConfig(alembic_ini_path)
        sync_url = self.url.set(drivername='sqlite+pysqlite')
        config.set_main_option('sqlalchemy.url', str(sync_url))
        alembic_command.upgrade(config, revisions)



    @classmethod
    def from_config(
        cls,
        config: SqliteOptions,
        *,
        is_testing: bool = False
    ) -> Self:
        url = create_url(is_testing=is_testing)
        engine = create_async_engine(url, **config.engine_kwargs)

        @event.listens_for(engine.sync_engine, 'connect')
        def _set_sqlite_pragmas(dbapi_conn, connection_record):
            add_sqlite_pragmas(dbapi_conn, config.pragmas)

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
