import logging
from typing import Final

from redis.asyncio import ConnectionPool as AsyncConnectionPool
from redis.asyncio import Redis as AsyncRedis

from server.configs.toml import RedisConfig
from server.settings import get_app_settings, get_secret_settings

logger = logging.getLogger(__name__)


def get_async_redis_pool(
    redis_url: str,
    *,
    options: RedisConfig | None = None,
) -> AsyncConnectionPool:
    """
    Creates a Redis async connection pool.

    Parameters
    ----------
    redis_url : str
        The Redis connection URL.
    options : RedisConfig | None, optional
        Additional Redis configuration options, by default None.

    Returns
    -------
    AsyncConnectionPool
        The created Redis async connection pool.
    """
    options = options or get_app_settings().redis
    return AsyncConnectionPool.from_url(
        redis_url,
        max_connections=options.max_connections,
        decode_responses=options.decode_responses,
        socket_timeout=options.socket_timeout,
        socket_connect_timeout=options.socket_connect_timeout,
        socket_keepalive=options.socket_keepalive,
        retry_on_timeout=options.retry_on_timeout,
        health_check_interval=options.health_check_interval,
    )


async_redis_pool: Final[AsyncConnectionPool] = get_async_redis_pool(
    get_secret_settings().get_redis_url()
)
redis_client: Final[AsyncRedis] = AsyncRedis(connection_pool=async_redis_pool)


async def ping_redis() -> bool:
    """
    Pings the Redis server to check connectivity.

    Returns
    -------
    bool
        True if the ping is successful, False otherwise.
    """
    logger.info('Pinging Redis server...')
    try:
        pong = await redis_client.ping()
        return bool(pong)
    except Exception as exc:
        logger.error('Redis could not be reached: %s', exc, exc_info=True)
        return False


async def disconnect_redis() -> None:
    """
    Closes the Redis client and disconnects the connection pool.
    """
    logger.info('Disconnecting Redis client and pool...')
    await redis_client.close()
    await async_redis_pool.disconnect()
    logger.info('Redis disconnected successfully.')
