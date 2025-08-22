

import contextlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import sqlparse
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import path_utils, settings
from app.core.model import MappedModel
from app.utils import import_utils

logger = logging.getLogger(__name__)

@dataclass(slots=True)
class SqlalchemyAdapter:
    url: URL
    engine: AsyncEngine
    session_local: async_sessionmaker[AsyncSession]

    @contextlib.asynccontextmanager
    async def connection(self):
        '''
        Yields a direct connection to the sqlalchemy engine.
        '''
        try:
            async with self.engine.begin() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Error during database connection: {e}", exc_info=e)
            raise

    @property
    def transaction(self) -> async_sessionmaker[AsyncSession]:
        """
        Returns a new transaction session.
        """
        return self.session_local

    @property
    def mapped_base(self) -> type[MappedModel]:
        """
        Returns the mapped base class for SQLAlchemy models.
        This is used to configure and map the models.
        """
        return MappedModel

    async def run_sql_file(self, sql_file: Path) -> None:
        if not sql_file.exists():
            raise FileNotFoundError(f"SQL file {sql_file} does not exist.")

        contents = sql_file.read_text()
        sql_text = []
        for statement in sqlparse.split(contents):
            if (stripped := statement.strip()):
                sql_text.append(text(stripped))

        async with self.connection() as conn:
            for statement in sql_text:
                logger.debug(f"Executing SQL statement: {statement}")
                await conn.execute(statement)


    async def set_sqlite_pragmas(self, conn: AsyncConnection) -> None:
        pragmas = settings.get_adapter_settings().sql.pragmas
        for cmd in pragmas.commands():
            logger.debug(f"Setting SQLite pragma: {cmd}")
            await conn.execute(text(cmd))

    async def register_models(self, conn: AsyncConnection) -> None:
        import_utils.load_mapped_models(root_package='app.api', module_basename='model')
        await conn.run_sync(self.mapped_base.metadata.create_all)





def _create_adapter(
    options: settings.AsyncEngineConfig | None = None
) -> SqlalchemyAdapter:

    config = settings.get_api_settings().db
    options = options or settings.get_adapter_settings().sql.async_engine
    url = URL.create(
        drivername=config.DRIVER_NAME,
        database=config.url_parts,
    )
    engine = create_async_engine(
        url,
        echo=config.ECHO,
        future=True,
        pool_size=options.pool_size,
        max_overflow=options.max_overflow,
        pool_timeout=options.pool_timeout,
        pool_recycle=options.pool_recycle,
        pool_pre_ping=options.pool_pre_ping,
        pool_use_lifo=options.pool_use_lifo,
        connect_args={
            'check_same_thread': False
        }
    )

    session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )

    return SqlalchemyAdapter(
        url=url,
        engine=engine,
        session_local=session_local
    )



_db_adapter: Final[SqlalchemyAdapter] = _create_adapter()

def get_adapter() -> SqlalchemyAdapter:
    """
    Returns the initialized SQLAlchemy adapter.
    """
    return _db_adapter

async def get_db() :
    """
    Provides a database session for dependency injection.
    This is used in FastAPI routes to access the database.
    """
    async with get_adapter().transaction() as session:
        yield session


async def connect_db() -> None:

    adapter = get_adapter()
    options = settings.get_adapter_settings().sql

    run_seed = False
    if (dirname := settings.get_api_settings().db.DIRECTORY):
        db_path = path_utils.abs_root_path(dirname)
        run_seed = db_path.exists()
        db_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Connecting to sqlite database at {db_path}")
    async with adapter.connection() as conn:
        await adapter.set_sqlite_pragmas(conn)

        await adapter.register_models(conn)

        if run_seed and options.seed_file:
            sql_file = path_utils.abs_root_path(options.seed_file)
            if sql_file.exists():
                logger.info(f"Running seed file: {sql_file}")
                await adapter.run_sql_file(sql_file)

    logger.info("Database connection established and models registered.")

async def disconnect_db() -> None:
    """
    Closes the database connection.
    This is called when the application shuts down.
    """
    await get_adapter().engine.dispose()
    logger.info("Database connection closed.")