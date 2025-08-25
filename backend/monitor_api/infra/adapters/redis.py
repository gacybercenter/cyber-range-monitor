from __future__ import annotations

import dataclasses
import logging
from typing import TYPE_CHECKING

import redis.asyncio as aioredis

from monitor_api.core.exceptions import AdapterConnectionError, AdapterNotConnectedError

if TYPE_CHECKING:
    from monitor_api.core.settings import RedisClientConfig

logger = logging.getLogger(__name__)


@dataclasses.dataclass(slots=True)
class RedisAdapter:
    url: str
    _pool: aioredis.ConnectionPool | None = dataclasses.field(default=None, init=False)
    _client: aioredis.Redis | None = dataclasses.field(default=None, init=False)

    async def connect(self, config: 'RedisClientConfig') -> None:
        """
        Connects to the Redis server using the provided configuration.

        Parameters
        ----------
        config : RedisClientConfig

        Raises
        ------
        AdapterConnectionError
            _If the connection attempt fails_
        """
        if self._pool and self._client:
            return
        logger.debug('Connecting to Redis...')
        self._pool = aioredis.ConnectionPool.from_url(
            self.url,
            **config.model_dump(),
            decode_responses=False,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)
        logger.debug('Created connection pool and client.')
        try:
            await self._client.ping()
        except aioredis.RedisError as ex:
            raise AdapterConnectionError(adapter_name='Redis', exc=ex) from ex
        logger.info('Connected to Redis successfully.')

    async def disconnect(self) -> None:
        """
        Disconnects the redis client and connection pool, if they exist.
        """
        if self._client:
            logger.info('Disconnecting Redis client...')
            await self._client.aclose()
            self._client = None
        if self._pool:
            logger.info('Disconnecting Redis connection pool...')
            await self._pool.disconnect()
            self._pool = None

    @property
    def client(self) -> aioredis.Redis:
        """
        Provides the connected Redis client instance.

        Returns
        -------
        aioredis.Redis

        Raises
        ------
        AdapterNotConnectedError
            _If the adapter was never connected_
        """
        if not self._client:
            raise AdapterNotConnectedError(adapter_name='Redis')
        return self._client
