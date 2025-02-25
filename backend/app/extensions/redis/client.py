import redis
import redis.exceptions

from .const import REDIS_CONFIG


redis_client = redis.Redis(
    host=REDIS_CONFIG.HOST,
    port=REDIS_CONFIG.PORT,
    db=REDIS_CONFIG.DB,
    password=REDIS_CONFIG.PASSWORD,
    decode_responses=True
)

def sanitize(key: str) -> str:
    return key.replace(":", "_")


async def is_connected() -> bool:
    '''Useful for debugging and testing purposes

    Returns:
        bool -- True if the Redis client is connected, False otherwise
    '''
    try:
        await redis_client.ping()
        return True
    except redis.exceptions.ConnectionError:
        return False
