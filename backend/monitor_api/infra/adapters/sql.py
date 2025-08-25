from __future__ import annotations

import contextlib
import logging
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING

import sqlparse
from sqlalchemy import URL, TextClause, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from monitor_api.core import import_utils
from monitor_api.core.exceptions import AdapterConnectionError, AdapterNotConnectedError

if TYPE_CHECKING:
    from pathlib import Path

    from monitor_api.core.settings import SqlalchemyConfig


logger = logging.getLogger(__name__)


def _parse_sql_file(raw_sql: str) -> list[TextClause]:
    statements = []
    for statement in sqlparse.split(raw_sql):
        if stripped_statement := statement.strip():
            statements.append(text(stripped_statement))
    return statements

@dataclass(slots=True)
class SqlitePragmas:
    journal_mode: str = 'WAL'
    synchronous: str = 'NORMAL'
    foreign_keys: int = 1
    temp_store: bool = True
    cache_size: int = -64_000  # 64MB

    def as_commands(self):
        for name, value in asdict(self).items():
            yield f'PRAGMA {name}={value};'



@dataclass(slots=True)
class SqlAdapter:
    """
    The main database adapter for handling connections
    and sessions
    """

    url: URL
    _engine: AsyncEngine | None = field(default=None, init=False)
    _session_local: async_sessionmaker[AsyncSession] | None = field(
        default=None, init=False
    )

    @contextlib.asynccontextmanager
    async def connection(self):
        """
        Async context manager that yields a database connection.

        Yields
        ------
        _AsyncConnection_

        Raises
        ------
        AdapterNotConnectedError
            _The adapter was not connected_
        AdapterConnectionError
            _An exception occured with the connection_
        """
        if not self._engine:
            raise AdapterNotConnectedError(adapter_name='SQL')
        try:
            logger.debug('Starting async database connection...')
            async with self._engine.begin() as conn:
                yield conn
        except Exception as e:
            logger.error(f'Error during database connection: {e}')
            raise AdapterConnectionError(
                adapter_name='SQL',
                exc=e
            ) from e

    async def register_models(self, conn: AsyncConnection) -> None:
        '''
        Registers all the models with the ORM, which creates the tables
        if they do not already exist or maps them to the existing tables.

        Parameters
        ----------
        conn : AsyncConnection
            _The current database connection_
        '''
        logger.info(
            'Registering databse models and creating tables if they do not exist...'
        )
        from monitor_api.core.model import MappedModel
        import_utils.load_mapped_models(auto_error=True)
        await conn.run_sync(MappedModel.metadata.create_all)

    async def set_pragmas(self, conn: AsyncConnection, pragmas: SqlitePragmas) -> None:
        '''
        Sets the pragmas for the current database connection.

        Parameters
        ----------
        conn : AsyncConnection
            _description_
        pragmas : SqlitePragmas
            _description_
        '''
        for command in pragmas.as_commands():
            logger.debug(f'Executing pragma command: {command}')
            await conn.execute(text(command))
        logger.info('Database pragmas set successfully.')

    async def connect(self, config: 'SqlalchemyConfig') -> None:
        """
        Initializes the database connection using the adapter,
        registers the models with the ORM and if the database
        file does not exist, runs the seed SQL file if provided.
        """
        if self._engine or self._session_local:
            return

        self._engine = create_async_engine(
            self.url,
            **config.engine_kwargs,
            connect_args={
                'check_same_thread': False,
                'timeout': config.timeout,
            },
        )
        self._session_local = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

        logger.info('Starting SQL database connection...')
        async with self.connection() as conn:
            await self.register_models(conn)

    async def disconnect(self) -> None:
        """
        Disposes of the database connection and session.
        """
        logger.debug('Disposing SQL database connection...')
        if self._engine:
            logger.info('Disposing SQL database connection...')
            await self._engine.dispose()
            self._engine = None
            self._session_local = None
            logger.info('SQL database connection disposed.')

    async def run_seed(self, sql_file_path: Path) -> None:
        """
        Executes the SQL statements in the provided file path.

        Parameters
        ----------
        sql_file_path : Path

        Raises
        ------
        AdapterNotConnectedError
            _If the adapter is not connected._
        AdapterConnectionError
            _If there is an error executing the SQL statements._
        """
        if not sql_file_path.exists():
            logger.warning(
                f'SQL file {sql_file_path} does not exist at path {sql_file_path}.'
                'Skipping execution.'
            )
            return
        contents = sql_file_path.read_text()
        statements = _parse_sql_file(contents)
        async with self.connection() as conn:
            for statement in statements:
                await conn.execute(statement)

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        if not self._session_local:
            raise AdapterNotConnectedError(adapter_name='SQL')
        return self._session_local
