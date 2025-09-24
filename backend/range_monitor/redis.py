

import logging
from dataclasses import dataclass
from typing import Self
from urllib.parse import quote_plus

from pydantic_settings import SettingsConfigDict
from redis import AuthenticationError, RedisError
from redis.asyncio import ConnectionPool, Redis

from range_monitor.core.config_class import EnvConfig, TomlSection

logger = logging.getLogger(__name__)

class RedisConfig(EnvConfig):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_'
    )

    host: str = 'localhost'
    port: int = 6379
    db: int = 0
    username: str | None = None
    password: str | None = None
    ssl: bool = False


class RedisOptions(TomlSection):
    '''config.toml -> [redis]'''
    socket_timeout: float = 5
    socket_connect_timeout: float = 5
    retry_on_timeout: bool = True
    health_check_interval: float = 10
    max_connections: int = 10


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
        encoded_username = quote_plus(config.username)
        encoded_password = quote_plus(config.password)
        auth_part = f'{encoded_username}:{encoded_password}@'

    elif config.password:
        encoded_password = quote_plus(config.password)
        auth_part = f':{encoded_password}@'

    return f'{scheme}://{auth_part}{config.host}:{config.port}/{config.db}'



@dataclass(slots=True)
class RedisConnection:
    '''
    An instance for managing the connection to the Redis server.

    '''
    pool: ConnectionPool
    client: Redis
    url: str


    async def is_alive(self) -> bool:
        '''
        Checks if the Redis server is reachable.

        Returns
        -------
        bool
        '''
        try:
            logger.info('Pinging Redis server...')
            response = await self.client.ping()
            return response is True
        except TimeoutError as e:
            logger.exception('Redis timeout error occurred.', exc_info=e)
        except AuthenticationError as e:
            logger.exception(
                'Redis authentication error occurred, ensure the credentials are valid',
                exc_info=e
            )
        except RedisError as e:
            logger.exception('A Redis error occurred.', exc_info=e)

        return False

    async def disconnect(self) -> None:
        logger.info('Disconnecting Redis client and pool...')
        await self.client.aclose()
        await self.pool.disconnect()

    @classmethod
    def from_config(
        cls,
        *,
        config: RedisConfig | None = None,
        options: RedisOptions | None = None,
    ) -> Self:
        '''
        Creates a Redis connection instance.

        Parameters
        ----------
        config : RedisConfig | None, optional
            The config to use, if omitted loads from env, by default None
        socket_timeout : float, optional
            The timeout for socket operations, by default 5.0
        socket_connect_timeout : float, optional
            The timeout for socket connections, by default 5.0
        retry_on_timeout : bool, optional
            Whether to retry on timeout, by default True
        health_check_interval : float, optional
            Specifies how often to check the health of the connection, by default 10.0
        max_connections : int, optional
            The maximum number of connections in the pool, by default 10

        Returns
        -------
        RedisConnection
        '''
        redis_config = config or RedisConfig()
        redis_options = options or RedisOptions()

        url = create_redis_url(redis_config)
        redis_pool = ConnectionPool.from_url(
            url,
            **redis_options.model_dump(),
            decode_responses=True,
        )
        redis_client = Redis(connection_pool=redis_pool)

        return cls(
            pool=redis_pool,
            client=redis_client,
            url=url
        )




