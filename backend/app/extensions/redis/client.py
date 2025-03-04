from typing import Optional

import redis
import redis.exceptions

from app import settings

config = settings.get_config_yml()
environment = config.app.environment


redis_client = redis.Redis(
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.db,
    password=settings.get_secrets().redis_password if environment != "local" else None,
    decode_responses=True,
)

# NOTE: the redis library has weird typing as sometimes
# it returns a coroutine and sometimes it doesn't meaning
# we have to use hasattr to check if it is a coroutine & await it
# if it is


def sanitize(key: str) -> str:
    return key.replace(":", "_")


async def is_connected() -> bool:
    """Useful for debugging and testing purposes

    Returns:
        bool -- True if the Redis client is connected, False otherwise
    """
    try:
        await redis_client.ping()
        return True
    except redis.exceptions.ConnectionError:
        return False


async def set_key(key: str, value: str, ex: Optional[int]) -> None:
    """Set a key in the Redis store

    Arguments:
        key {str} -- the key to store the value under
        value {str} -- the value to store

    Keyword Arguments:
        ex {int} -- optional expiration time (default: {0})
    """
    result = redis_client.set(key, value, ex=ex)
    if hasattr(result, "__await__"):
        await result


async def get_key(key: str) -> Optional[str]:
    """Get a key from the Redis store

    Arguments:
        key {str} -- the key to get the value from

    Returns:
        Optional[str] -- the value if it exists
    """
    result = redis_client.get(key)
    if hasattr(result, "__await__"):
        result = await result

    return result  # type: ignore


async def delete_key(key: str) -> None:
    """delete a key from the Redis store

    Arguments:
        key {str} -- the key to delete
    """

    result = redis_client.delete(key)
    if hasattr(result, "__await__"):
        await result


async def set_expiration(key: str, ex: int) -> None:
    """Set the expiration time for a key

    Arguments:
        key {str} -- the key to set the expiration time for
        ex {int} -- the expiration time in seconds
    """
    result = redis_client.expire(key, ex)
    if hasattr(result, "__await__"):
        await result
