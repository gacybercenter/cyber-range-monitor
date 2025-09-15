from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, TypedDict, Unpack
from venv import logger

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from range_monitor import constant
from range_monitor.adapters.interface import ConnectableAdapter
from range_monitor.model import MappedModel

if TYPE_CHECKING:
    from range_monitor.core.crypto import PasswordHashes

class SqlConnectionOptions(TypedDict, total=False):
    '''
    optional default parameters for SQLAlchemy connection pool
    of the database engine

    Attributes
    ----------
    - pool_size : int
        The size of the database connection pool. Default is 5.
    - max_overflow : int
        The maximum number of connections to allow in connection pool overflow.
        Default is 10.
    - pool_timeout : int
        The number of seconds to wait before giving up on getting a connection
        from the pool. Default is 30.
    - pool_recycle : int
        The number of seconds after which a connection is automatically recycled.
        Default is 1800 (30 minutes).
    - pool_pre_ping : bool
        If True, the connection pool will emit a "ping" (SELECT 1) to test
        connections before using them. Default is True.
    - pool_use_lifo : bool
        If True, the connection pool will use a LIFO strategy for connection
        pooling. Default is False (FIFO).
    - echo : bool
        If True, the engine will log all statements as well as a repr() of
        their parameter lists to the default log handler, which defaults to
        sys.stdout. Default is False.
    - timeout : int
        The timeout value for the database connection in seconds. Default is 30.
    - expire_on_commit : bool
        If True, all instances will be fully expired after each commit.
        Default is False.
    - autoflush : bool
        If True, the Session will automatically flush all pending changes
        to the database before each query. Default is False.

    '''
    pool_size: int
    max_overflow: int
    pool_timeout: int
    pool_recycle: int
    pool_pre_ping: bool
    pool_use_lifo: bool
    echo: bool
    timeout: int
    expire_on_commit: bool
    autoflush: bool


async def register_models(conn: AsyncConnection) -> None:
    logger.info('Creating database tables if they do not exist...')
    await conn.run_sync(MappedModel.metadata.create_all)

async def set_sqlite_pragmas(conn: AsyncConnection) -> None:
    for name, value in constant.SQLITE_PRAGMAS.items():
        logger.debug(f'Setting SQLite PRAGMA {name}={value}')
        await conn.execute(text(f'PRAGMA {name}={value};'))


def create_sqlite_url(is_testing: bool = False) -> URL:
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

class SqliteConnection(ConnectableAdapter):

    def __init__(self, is_testing: bool = False) -> None:
        self.url: URL = create_sqlite_url(is_testing)
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None


    def open(self, **sql_options: Unpack[SqlConnectionOptions]) -> None:
        '''
        Opens a database connection with the given parameters
        and creates the async engine and sessionmaker.

        Parameters
        ----------
        sql_options : SqlConnectionOptions
            Optional parameters for SQLAlchemy connection pool with default values.
        '''
        constant.DATABASE_DIR_PATH.mkdir(parents=True, exist_ok=True)

        engine_kwargs = {
            'echo': sql_options.get('echo', False),
            'pool_size': sql_options.get('pool_size', 5),
            'max_overflow': sql_options.get('max_overflow', 10),
            'pool_timeout': sql_options.get('pool_timeout', 30),
            'pool_recycle': sql_options.get('pool_recycle', 1800),
            'pool_pre_ping': sql_options.get('pool_pre_ping', True),
            'pool_use_lifo': sql_options.get('pool_use_lifo', False),
            'future': True,
        }


        self._engine = create_async_engine(
            self.url,
            connect_args={
                'timeout': sql_options.get('timeout', 30),
                'check_same_thread': False,
            },
            **engine_kwargs,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            expire_on_commit=sql_options.get('expire_on_commit', False),
            autoflush=sql_options.get('autoflush', True),
            class_=AsyncSession,
        )

    @asynccontextmanager
    async def orm_engine(self):
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

    async def connect(self) -> None:
        '''
        Connects to the database and sets pragmas and creates tables.

        Raises
        ------
        RuntimeError
            _The database was never opened_
        '''
        async with self.orm_engine() as conn:
            await set_sqlite_pragmas(conn)
            await register_models(conn)

    async def disconnect(self) -> None:
        '''
        Closes the database connection and disposes of the engine.
        '''
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

    def is_open(self) -> bool:
        return self._engine is not None and self._sessionmaker is not None