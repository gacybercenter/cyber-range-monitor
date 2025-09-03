import dataclasses
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from venv import logger

import sqlparse
from sqlalchemy import URL, TextClause, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from range_monitor import constant
from range_monitor.model import MappedModel

if TYPE_CHECKING:
    from range_monitor.core.crypto import PasswordHashes

@dataclasses.dataclass(slots=True)
class SqlalchemyPoolOptions:
    '''
    optional default parameters for SQLAlchemy connection pool
    of the database engine
    '''
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 1800
    pool_pre_ping: bool = True
    pool_use_lifo: bool = False




class DatabaseUtils:

    @staticmethod
    async def register_models(conn: AsyncConnection) -> None:
        logger.info('Creating database tables if they do not exist...')
        await conn.run_sync(MappedModel.metadata.create_all)

    @staticmethod
    def parse_sql_string(raw_sql: str) -> list[TextClause]:
        statements = []
        for statement in sqlparse.split(raw_sql):
            if stripped_statement := statement.strip():
                statements.append(text(stripped_statement))
        return statements

    @staticmethod
    async def set_sqlite_pragmas(conn: AsyncConnection) -> None:
        for name, value in constant.SQLITE_PRAGMAS.items():
            logger.debug(f'Setting SQLite PRAGMA {name}={value}')
            await conn.execute(text(f'PRAGMA {name}={value};'))




@dataclasses.dataclass(slots=True)
class SqliteConnection:
    _engine: AsyncEngine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None


    def create_url(self, *, is_testing: bool = False) -> URL:
        if is_testing:
            return URL.create(
                drivername=constant.DATABASE_DRIVER,
                database=':memory:',
            )
        else:
            return URL.create(
                drivername=constant.DATABASE_DRIVER,
                database=f'{constant.DATABASE_DIRNAME}/{constant.DATABASE_FILE_NAME}',
            )

    def open(
        self,
        *,
        is_testing: bool = False,
        echo: bool = False,
        timeout: int = 30,
        pool_options: SqlalchemyPoolOptions | None = None,
    ) -> None:
        '''
        Opens a database connection with the given parameters
        and creates the async engine and sessionmaker.

        Parameters
        ----------
        is_testing : bool, optional
            _if is_testing is true it uses an in memory database_, by default False
        echo : bool, optional
            _echo sql statements, very verbose_, by default False
        timeout : int, optional
            _timeout in seconds for idle sessions_, by default 30
        '''
        constant.DATABASE_DIR_PATH.mkdir(parents=True, exist_ok=True)
        pool_options = pool_options or SqlalchemyPoolOptions()

        url = self.create_url(is_testing=is_testing)
        self._engine = create_async_engine(
            url,
            echo=echo,
            connect_args={'timeout': timeout, 'check_same_thread': False},
            **dataclasses.asdict(pool_options),
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def engine(self):
        '''
        Context manager that yields a database connection
        and ensures the connection was properly opened.
        Raises
        ------
        RuntimeError
            _The database was never opened_
        '''
        if not self._engine:
            raise RuntimeError('Database connection is not open.')
        logger.info('Acquiring database engine connection...')
        async with self._engine.begin() as conn:
            yield conn

    @property
    def session_local(self) -> async_sessionmaker[AsyncSession]:
        if not self._sessionmaker:
            raise RuntimeError('Database connection was never opened.')
        return self._sessionmaker

    async def disconnect(self) -> None:
        logger.info('Closing database connection...')
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info('Database connection closed.')

    async def seed(self, hasher: 'PasswordHashes') -> None:
        '''
        Seeds the database with default users, for development
        only. Each user created has a username of their role
        and a password of their role and a role of (you guessed it)
        their role.

        Parameters
        ----------
        hasher : PasswordHashes
        '''
        from range_monitor.utils import seed

        async with self.session_local() as db:
            await seed.seed_default_users(hasher, db)
            await db.commit()

    async def connect(self) -> None:
        '''
        Connects to the database and sets pragmas and creates tables.

        Raises
        ------
        RuntimeError
            _The database was never opened_
        '''
        async with self.engine() as conn:
            await DatabaseUtils.set_sqlite_pragmas(conn)
            await DatabaseUtils.register_models(conn)