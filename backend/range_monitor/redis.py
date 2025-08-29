

import dataclasses
from urllib.parse import quote_plus

import redis.asyncio as aioredis
from pydantic_settings import SettingsConfigDict

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

    def create_url(self) -> str:
        scheme = 'rediss' if self.ssl else 'redis'

        auth_part = ''
        if self.username and self.password:
            encoded_username = quote_plus(self.username)
            encoded_password = quote_plus(self.password)
            auth_part = f'{encoded_username}:{encoded_password}@'

        elif self.password:
            encoded_password = quote_plus(self.password)
            auth_part = f':{encoded_password}@'

        return f'{scheme}://{auth_part}{self.host}:{self.port}/{self.db}'

@dataclasses.dataclass(slots=True)
class RedisClientOptions:
    # timeout for socket operations in seconds
    socket_timeout: float = 5.0
    # timeout for establishing socket connections in seconds
    socket_connect_timeout: float = 5.0
    # whether to retry operations when a timeout occurs
    retry_on_timeout: bool = True
    # interval between health checks in seconds
    health_check_interval: float = 10.0
    # maximum number of connections in the pool
    max_connections: int = 10


@dataclasses.dataclass(slots=True)
class RedisConnection:
    _pool: aioredis.ConnectionPool | None = None
    _client: aioredis.Redis | None = None


    def open(
        self,
        *,
        config: RedisConfig | None = None,
        options: RedisClientOptions | None = None
    ) -> None:
        '''
        Opens the redis connection pool and creates a client from it

        Parameters
        ----------
        url : str
        options : RedisClientOptions
        '''
        if self._pool and self._client:
            return

        options = options or RedisClientOptions()
        config = config or RedisConfig()
        config = RedisConfig()
        self._pool = aioredis.ConnectionPool.from_url(
            config.create_url(),
            **dataclasses.asdict(options),
            decode_responses=True,
        )
        self._client = aioredis.Redis(connection_pool=self._pool)

    @property
    def client(self) -> aioredis.Redis:
        if not self._client:
            raise RuntimeError('Redis client was never connected.')
        return self._client

    @property
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
