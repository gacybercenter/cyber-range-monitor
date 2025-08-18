import contextlib
import logging
from collections.abc import AsyncGenerator
from typing import Final
from urllib.parse import quote_plus

import redis.asyncio as aioredis
from redis.exceptions import AuthenticationError, TimeoutError

from .exceptions import RedisConnectionFailed, RedisPoolNotInitializedError
from .settings import RedisClientOptions, RedisSecrets, redis_options, redis_secrets

logger = logging.getLogger(__name__)


def create_redis_url(
    *,
    host: str,
    port: int,
    db: int,
    username: str | None = None,
    password: str | None = None,
    ssl: bool = False,
) -> str:
    scheme = 'rediss' if ssl else 'redis'

    auth_part = ''
    if username and password:
        encoded_username = quote_plus(username)
        encoded_password = quote_plus(password)
        auth_part = f'{encoded_username}:{encoded_password}@'
    elif password:
        encoded_password = quote_plus(password)
        auth_part = f':{encoded_password}@'

    url = f'{scheme}://{auth_part}{host}:{port}/{db}'

    return url



class _RedisConnection:
    def __init__(
        self,
        *,
        options: RedisClientOptions,
        secrets: RedisSecrets,
    ) -> None:
        self.redis_url: str = create_redis_url(
            host=secrets.HOST,
            port=secrets.PORT,
            db=secrets.DB,
            username=secrets.USERNAME,
            password=secrets.PASSWORD,
        )
        self._pool: aioredis.ConnectionPool | None = None
        self._pool_options: dict = {
            **options.model_dump(exclude_unset=True),
            'decode_responses': True,
        }
        self.logger = logging.getLogger(__name__)

    def update_pool_options(self, **kwargs: str | int | bool) -> None:
        """
        Updates the Redis connection pool options.

        Parameters
        ----------
        **kwargs : str | int | bool
            The options to update in the Redis connection pool.
        """
        self._pool_options.update(kwargs)


    @contextlib.asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[aioredis.Redis, None]:
        '''
        Creates and yields a Redis client from the connection pool.

        Returns
        -------
        AsyncGenerator[aioredis.Redis, None]

        Yields
        ------
        Iterator[AsyncGenerator[aioredis.Redis, None]]

        Raises
        ------
        RedisPoolNotInitializedError
        '''
        if self._pool is None:
            raise RedisPoolNotInitializedError()

        self.logger.debug('Acquiring Redis client from connection pool...')
        client = aioredis.Redis(connection_pool=self._pool)
        try:
            yield client
        finally:
            await client.aclose()

    async def heartbeat(self, *, auto_error: bool = False) -> bool:
        '''
        Checks the health of the Redis connection by sending a PING command,
        returns True if the connection is healthy. Only raises if `auto_error`
        is True.

        Parameters
        ----------
        auto_error : bool, optional

        Returns
        -------
        bool

        Raises
        ------
        RedisPoolNotInitializedError
        RedisConnectionFailed
        '''
        if self._pool is None:
            raise RedisPoolNotInitializedError()

        try:
            async with self.get_connection() as conn:
                pong = await conn.ping()
                return pong is True
        except (TimeoutError, AuthenticationError) as e:
            if auto_error:
                raise RedisConnectionFailed(
                    reason='Failed to ping Redis Client during heartbeat check.',
                    exc=e
                ) from e

            return False

    async def connect(self) -> None:
        logger.info('Attempting to connect to redis')
        if self._pool is not None:
            logger.warning(
                'Redis connection pool already exists, it should only be created once.'
            )
            return
        self._pool = aioredis.ConnectionPool.from_url(
            url=self.redis_url,
            **self._pool_options,
        )
        await self.heartbeat(auto_error=True)

    async def disconnect(self) -> None:
        if self._pool is None:
            logger.warning('Redis connection pool was never initialized.')
            return

        logger.info('Disconnecting from Redis...')
        await self._pool.disconnect()
        self._pool = None
        logger.info('Redis disconnected.')

RedisConnection: Final[_RedisConnection] = _RedisConnection(
    secrets=redis_secrets,
    options=redis_options,
)