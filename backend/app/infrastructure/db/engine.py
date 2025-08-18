import contextlib
import logging
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any, Final

import aiosqlite
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import path_utils
from app.infrastructure.db.model import MappedBase

from . import const
from .settings import DatabaseSecrets, SQLAlchemyOptions, db_secrets, sqlalchemy_options


class _DatabaseEngine:
    def __init__(
        self,
        *,
        sqlalchemy_config: SQLAlchemyOptions | None = None,
        secrets: DatabaseSecrets | None = None,
    ) -> None:
        sqlalchemy_config = sqlalchemy_config or sqlalchemy_options
        secret_settings = secrets or db_secrets

        self._url = URL.create(
            drivername=const.DB_DRIVER_NAME,
            database=secret_settings.database,
        )

        self._async_engine: AsyncEngine = create_async_engine(
            url=self._url,
            echo=secret_settings.ECHO,
            connect_args=const.CONNECT_ARGS,
            **sqlalchemy_options.engine_kwargs,
        )

        self._session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=sqlalchemy_options.expire_on_commit,
            autoflush=sqlalchemy_options.autoflush,
            class_=AsyncSession,
        )

        self.secrets: DatabaseSecrets = secret_settings
        self.logger = logging.getLogger(__name__)
        self.run_seed: bool = sqlalchemy_options.run_seed

    @contextlib.asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provides a database session to the caller within a context manager.

        Returns
        -------
        AsyncSession

        Yields
        ------
        Iterator[AsyncSession]
        """
        async with self._session_maker() as session:
            yield session


    async def _register_models(self, conn: AsyncConnection) -> None:
        from . import _mapped_models  # noqa: F401

        await conn.run_sync(MappedBase.metadata.create_all)

    async def _set_sqlite3_pragmas(
        self,
        conn: AsyncConnection,
        *,
        pragamas: dict[str, Any] | None = None,
    ) -> None:
        pragmas = pragamas or const.PRAGMAS
        for pragma, value in pragmas.items():
            pragma_statement = text(f'PRAGMA {pragma} = {value}')
            await conn.execute(pragma_statement)
        self.logger.info('SQLite PRAGMAs set successfully.')

    async def connect(
        self,
        *,
        seed_db: bool | None = None,
    ) -> None:
        """
        Starts the database connection, sets the SQLite PRAGMAs, and
        registers the models with the ORM

        Parameters
        ----------
        seed_db : bool | None, optional
            _Defaults to the option `sqlalchemy_options.run_seed`_, by default None
        """
        if self.secrets.FILE_NAME != ':memory:':
            self.db_dir.mkdir(exist_ok=True)

        if seed_db is None:
            seed_db = self.run_seed

        async with self._async_engine.begin() as conn:
            await self._set_sqlite3_pragmas(conn)
            self.logger.info('Registering database models w/ SQLAlchemy')
            await self._register_models(conn)

        if seed_db:
            self.logger.info('Seeding database...')
            await self.seed_database()

    async def disconnect(self) -> None:
        self.logger.info('Disconnecting from the database...')
        await self._async_engine.dispose()
        self.logger.info('Database connection closed.')

    async def seed_database(self) -> None:
        """Seeds the database with initial data."""
        from .seed import get_seed_data

        data = get_seed_data()
        async with self._session_maker() as session:
            for seeds in data:
                session.add_all(seeds)
            await session.commit()
        self.logger.info('Database seeded successfully.')

    async def get_server_version(self) -> Any:
        """Returns the server version of the database."""
        async with self._session_maker() as session:
            result = await session.execute(text('SELECT sqlite_version()'))
            return result.scalar()

    @property
    def db_dir(self) -> Path:
        return path_utils.get_app_root().joinpath(self.secrets.DIRECTORY)

    @property
    def url(self) -> URL:
        return self._url

    @property
    def driver(self) -> str:
        return f'{self.secrets.DRIVER_NAME} {aiosqlite.__version__}'


DatabaseEngine: Final[_DatabaseEngine] = _DatabaseEngine()
