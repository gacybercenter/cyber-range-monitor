from __future__ import annotations

import logging
from dataclasses import dataclass

import redis.asyncio as aioredis

from range_monitor.
from range_monitor.db.repo import SqliteConnection, create_sqlite_connection
from range_monitor.redis import RedisConnection, create_redis_connection
from range_monitor.security import SecurityPolicy

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ServerResources:
    """
    The resources that are shared via the lifespan context manager,
    not an actual type, more of a type hint for use in dependency injection.
    """

    redis_client: aioredis.Redis
    sql: SqliteConnection
    security_policy: SecurityPolicy



class ServerLifespan:

    def __init__(self, config: RangeMonitorSettings) -> None:
        logger.info('Server lifespan initializing...')
        self._db: SqliteConnection = create_sqlite_connection(
            echo=config.sql.echo,
            pool_pre_ping=config.sql.pool_pre_ping,
            pool_recycle=config.sql.pool_recycle,
            is_testing=config.app.testing,
        )
        self._redis: RedisConnection = create_redis_connection(
            socket_timeout=config.redis.socket_timeout,
            socket_connect_timeout=config.redis.socket_connect_timeout,
            retry_on_timeout=config.redis.retry_on_timeout,
            health_check_interval=config.redis.health_check_interval,
            max_connections=config.redis.max_connections,
        )
        if config.app.testing:
            self._security = SecurityPolicy.testing_policy()
        else:
            self._security = SecurityPolicy()

    async def startup(self) -> ServerResources:
        logger.info('Server lifespan starting up...')
        from range_monitor.utils import seed
        await self._db.create_tables()

        async with self._db.session() as session:
            await seed.insert_default_users(
                self._security.passwords,
                session
            )

        if not await self._redis.is_alive():
            raise ConnectionError('Could not connect to Redis server.')

        return ServerResources(
            redis_client=self._redis.client,
            db_session=self._db,
            security_policy=self._security
        )

    async def shutdown(self) -> None:
        logger.info('Server lifespan shutting down...')
        if self._db:
            await self._db.disconnect()

        if self._redis:
            await self._redis.disconnect()

