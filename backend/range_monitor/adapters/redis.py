

from typing import TypedDict, Unpack
from urllib.parse import quote_plus

import redis.asyncio as aioredis
from pydantic_settings import SettingsConfigDict

from range_monitor.adapters.interface import ConnectableAdapter
from range_monitor.core.config_class import EnvConfig


class RedisConfig(EnvConfig):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
    )

    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    username: str | None = None
    password: str | None = None
    ssl: bool = False



class RedisOptions(TypedDict, total=False):
    '''
    Optional parameters for Redis connection pool

    Parameters
    ----------
    socket_timeout : float
        The timeout for socket operations in seconds. Default is 5.0 seconds.
    socket_connect_timeout : float
        The timeout for establishing a connection in seconds. Default is 5.0 seconds.
    retry_on_timeout : bool
        Whether to retry commands if a timeout occurs. Default is True.
    health_check_interval : float
        The interval in seconds for health checks of the connection.
        Default is 10.0 seconds.
    max_connections : int
        The maximum number of connections in the pool. Default is 10.
    '''
    socket_timeout: float
    socket_connect_timeout: float
    retry_on_timeout: bool
    health_check_interval: float
    max_connections: int


def create_redis_url(config: RedisConfig) -> str:

    scheme = 'rediss' if config.ssl else 'redis'

    auth_part = ''
    if config.username and config.password:
        encoded_username = quote_plus(config.username)
        encoded_password = quote_plus(config.password)
        auth_part = f'{encoded_username}:{encoded_password}@'

    elif config.password:
        encoded_password = quote_plus(config.password)
        auth_part = f':{encoded_password}@'

    return f'{scheme}://{auth_part}{config.host}:{config.port}/{config.db}'


class RedisConnection(ConnectableAdapter):
    def __init__(self, redis_config: RedisConfig | None = None) -> None:
        self.config = redis_config or RedisConfig()
        self._pool: aioredis.ConnectionPool | None = None
        self._client: aioredis.Redis | None = None

    def open(self, **options: Unpack[RedisOptions]) -> None:
        '''
        Opens the redis connection pool and creates a client from it

        Parameters
        ----------
        options : RedisOptions
            Optional parameters for Redis connection pool with default values.
        '''
        if self._pool and self._client:
            return

        self._pool = aioredis.ConnectionPool.from_url(
            create_redis_url(self.config),
            socket_timeout=options.get('socket_timeout', 5.0),
            socket_connect_timeout=options.get('socket_connect_timeout', 5.0),
            retry_on_timeout=options.get('retry_on_timeout', True),
            health_check_interval=options.get('health_check_interval', 10.0),
            max_connections=options.get('max_connections', 10),
            decode_responses=True,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)

    def is_open(self) -> bool:
        return self._client is not None and self._pool is not None

    async def disconnect(self) -> None:
        '''
        Closes the connected client and pool if they were connected.
        '''
        if self._client:
            await self._client.aclose()
            self._client = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None

    async def connect(self) -> None:
        '''
        Reconnects the client if it was disconnected.
        '''
        if not self._pool or not self._client:
            raise RuntimeError('Redis connection was never opened, call open() first.')
        try:
            await self._client.ping()
        except aioredis.RedisError as ex:
            await self.disconnect()
            raise RuntimeError('Failed to connect to Redis.') from ex

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError('Redis client was never connected.')
        return self._client
