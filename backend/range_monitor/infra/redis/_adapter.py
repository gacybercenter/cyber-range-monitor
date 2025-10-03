'''
An implementation of an adapter used to manage the lifespan
of the Redis connection pool and client throughout the application.

Raises
------
RuntimeAppError
    - If the Redis connection fails or an error occurs.
    - If the Redis connection is already open when attempting to open it again.
    - If the Redis connection is not open when attempting to use the client.
'''

import dataclasses as dc
import logging
import urllib.parse
from typing import Self, TypeAlias

from redis import AuthenticationError, RedisError
from redis.asyncio import ConnectionPool, Redis

from range_monitor.core.errors import RuntimeAppError
from range_monitor.infra.redis._config import RedisConfig, RedisOptions

logger = logging.getLogger(__name__)


def create_redis_url(config: RedisConfig) -> str:
    '''
    Creates a Redis connection URL from the given configuration.

    Parameters
    ----------
    config : RedisConfig

    Returns
    -------
    str
    '''
    scheme = 'rediss' if config.ssl else 'redis'

    auth_part = ''
    if config.username and config.password:
        encoded_username = urllib.parse.quote_plus(config.username)
        encoded_password = urllib.parse.quote_plus(config.password)
        auth_part = f'{encoded_username}:{encoded_password}@'

    elif config.password:
        encoded_password = urllib.parse.quote_plus(config.password)
        auth_part = f':{encoded_password}@'

    return f'{scheme}://{auth_part}{config.host}:{config.port}/{config.db}'

RedisExceptions: TypeAlias = AuthenticationError | RedisError | Exception

def _get_redis_exception(err: RedisExceptions) -> Exception:
    if isinstance(err, AuthenticationError):
        return RuntimeAppError('Redis authentication failed.')
    elif isinstance(err, RedisError):
        return RuntimeAppError('Redis error occurred.')
    else:
        return RuntimeAppError('An unexpected error occurred with Redis.')


@dc.dataclass(slots=True)
class RedisDatabase:
    '''
    A Redis database adapter that manages the connection pool and client.

    Raises
    ------
    RuntimeAppError
    '''
    _pool: ConnectionPool | None = dc.field(
        default=None,
        repr=False,
        init=False
    )
    _client: Redis | None = dc.field(
        default=None,
        repr=False,
        init=False
    )

    url: str = dc.field(repr=False, default='localhost')
    options: RedisOptions = dc.field(default_factory=RedisOptions)

    @classmethod
    def from_config(
        cls,
        *,
        config: RedisConfig | None = None,
        options: RedisOptions | None = None
    ) -> Self:
        '''
        Creates a RedisDatabase instance from the given configuration.

        Parameters
        ----------
        config : RedisConfig | None, optional
            The Redis configuration, by default None
        options : RedisOptions | None, optional
            The Redis connection options, by default None

        Returns
        -------
        Self
        '''
        redis_config = config or RedisConfig()
        url = create_redis_url(redis_config)

        return cls(
            url=url,
            options=options or RedisOptions()
        )



    def open(self) -> None:
        '''
        Opens the Redis Connection Poool and
        creates a client for it.

        Raises
        ------
        RuntimeAppError
            If the Redis connection is already open.
        '''
        if self._client or self._pool:
            raise RuntimeAppError(
                code='redis_already_connected',
                reason='Redis connection is already open.',
                fix='Close the existing connection before opening a new one.'
            )

        self._pool = ConnectionPool.from_url(
            self.url,
            **self.options.model_dump(),
            decode_responses=True
        )
        self._client = Redis(connection_pool=self._pool)

    def get_client(self) -> Redis:
        '''
        Gets the Redis client.

        Returns
        -------
        Redis

        Raises
        ------
        RuntimeAppError
            If the Redis connection was never opened
        '''
        if not self._client or not self._pool:
            raise RuntimeAppError(
                code='redis_not_connected',
                reason='Redis connection is not open.',
                fix='Call `open()` to establish a connection before using the client.'
            )

        return self._client

    def is_open(self) -> bool:
        '''
        Checks if the Redis connection and pool are open.

        Returns
        -------
        bool
        '''
        return self._client is not None and self._pool is not None


    async def aconnect(self) -> None:
        '''
        Opens the Redis connection and pool asynchronously
        and verifies the connection by pinging the server.

        Raises
        ------
        RuntimeAppError
            If the Redis connection fails or an error occurs.
        '''
        if not self.is_open():
            self.open()

        logger.info('Pinging redis client...')
        try:
            await self.get_client().ping()
        except (AuthenticationError, RedisError, Exception) as err:
            raise _get_redis_exception(err) from err

        logger.info('Redis client is reachable.')


    async def adisconnect(self) -> None:
        '''
        Closes the Redis connection and pool asynchronously.
        '''
        if self._client:
            await self._client.close()
            self._client = None

        if self._pool:
            await self._pool.disconnect()
            self._pool = None

