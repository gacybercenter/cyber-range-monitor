from __future__ import annotations

import logging
from dataclasses import asdict, dataclass

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from range_monitor import log
from range_monitor.config import RangeMonitorSettings, get_app_settings
from range_monitor.db import SqliteConnection
from range_monitor.redis import RedisConnection
from range_monitor.security import (
    Encryptor,
    PasswordHashes,
    SignatureProvider,
    create_security_services,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class APIResources:
    """
    The resources that are shared via the lifespan context manager.
    """

    redis: aioredis.Redis
    db: async_sessionmaker[AsyncSession]
    passwords: PasswordHashes
    encryptor: Encryptor
    signatures: SignatureProvider

    def dump(self) -> dict:
        return asdict(self)


class ServerContext:
    """
    Context and state the must be constructed at runtimed
    or singletons created once.
    """

    def __init__(self, *, is_testing: bool = False) -> None:
        security_bundle = create_security_services(is_testing=is_testing)
        self.passwords: PasswordHashes = security_bundle.passwords
        self.encryptor: Encryptor = security_bundle.encryptor
        self.signatures: SignatureProvider = security_bundle.signatures
        self.db: SqliteConnection = SqliteConnection()
        self.redis: RedisConnection = RedisConnection()
        logger.info('Server context initialized.')

    def open_connections(self, settings: RangeMonitorSettings) -> None:
        """
        Opens connections to the database and redis.

        Parameters
        ----------
        settings : RangeMonitorSettings
        """
        self.db.open(
            is_testing=settings.app.testing,
            echo=settings.sql.echo,
            timeout=settings.sql.timeout,
        )
        self.redis.open()

    async def connect(self) -> None:
        """
        The startup for the application.
        """
        await self.db.connect()
        logger.info('SQLite connection established.')

        await self.redis.connect()
        logger.info('Redis connection established.')

        if get_app_settings().app.debug:
            await self.db.seed_users(self.passwords)
            logger.info('Database seeded with initial data.')

        logger.info('All adapters connected.')

    async def disconnect(self) -> None:
        """
        What runs when the application is shutting down.
        """
        await self.db.disconnect()
        logger.info('SQLite connection closed.')

        await self.redis.disconnect()
        logger.info('Redis connection closed.')

        logger.info('All adapters disconnected.')
        log.clear_sinks()

    @property
    def resources(self) -> APIResources:
        """
        The resources that are shared via the lifespan context manager.
        """
        return APIResources(
            redis=self.redis.client,
            db=self.db.session_local,
            passwords=self.passwords,
            encryptor=self.encryptor,
            signatures=self.signatures,
        )
