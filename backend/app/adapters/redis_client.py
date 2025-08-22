import logging
from dataclasses import dataclass
from typing import Final
from urllib.parse import quote_plus

import redis.asyncio as aioredis

from app.core import settings

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


@dataclass(slots=True)
class AsyncRedisAdapter:
    url: str
    pool: aioredis.ConnectionPool


    def make_client(self, **overrides) -> aioredis.Redis:
        """
        Creates a Redis client with the specified overrides.
        """
        client = aioredis.Redis(
            connection_pool=self.pool,
            **overrides
        )
        return client


def _create_adapter() -> AsyncRedisAdapter:


    options = settings.get_adapter_settings().redis_client
    config = settings.get_api_settings().redis
    url = create_redis_url(
        host=config.HOST,
        port=config.PORT,
        db=config.DB,
        username=config.USERNAME,
        password=config.PASSWORD,
    )

    pool = aioredis.ConnectionPool.from_url(
        url,
        decode_responses=True,
        **options.model_dump()
    )

    return AsyncRedisAdapter(
        url=url,
        pool=pool
    )

_redis_adapter: Final[AsyncRedisAdapter] = _create_adapter()


def get_adapter() -> AsyncRedisAdapter:
    """
    Returns the initialized Redis adapter.
    """
    return _redis_adapter

async def get_redis_client():
    """
    Returns a Redis client from the adapter's connection pool.
    """
    client = get_adapter().make_client()
    logger.info(f"Acquired Redis client: {client}")
    try:
        yield client
    finally:
        logger.info("Closing Redis client connection.")
        await client.aclose()

async def connect_redis() -> None:
    '''
    Connects to redis by pinging a client created
    by the adapter.
    '''

    logger.info("Connecting to Redis...")
    client = get_adapter().make_client()
    try:
        await client.ping()
    except Exception as e:
        logger.error(
            'Could not connect to redis, your config is likely incorrect, '
            f'ensure it is running and reachable: {e}'
        )
        raise
    finally:
        await client.aclose()


async def disconnect_redis() -> None:
    """
    Closes the Redis connection pool.
    """
    await _redis_adapter.pool.disconnect()