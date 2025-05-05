
import logging
import sys
from redis.asyncio import Redis
from redis.exceptions import TimeoutError, AuthenticationError

from app.core import settings

from .config import redis_settings
from .const import (
    SOCKET_CONNECT_TIMEOUT,
    SOCKET_TIMEOUT,
    MAX_CONNECTIONS,
    HEALTH_CHECK_INTERVAL
)


logger = logging.getLogger(__name__)


def fail(reason: str) -> None:
    '''Fail the application with a reason.'''
    logger.error(reason)
    sys.exit(1)

class RedisClient(Redis):
    '''Pre-configured wrapper class for the Redis Client'''
    def __init__(self) -> None:
        password = None
        if redis_settings.use_password:
            password = settings.get_secret_settings().redis_password
        super(RedisClient, self).__init__(
            host=redis_settings.host,
            port=redis_settings.port,
            db=redis_settings.db,
            socket_connect_timeout=SOCKET_CONNECT_TIMEOUT,
            socket_timeout=SOCKET_TIMEOUT,
            max_connections=MAX_CONNECTIONS,
            health_check_interval=HEALTH_CHECK_INTERVAL,
            decode_responses=True,
            password=password
        )

    async def open(self) -> None:
        '''Open the Redis connection and check if it is reachable.'''
        try:
            await self.ping()
        except TimeoutError:
            fail("RedisError: Client connection timed out and could not be reached")
        except AuthenticationError:
            fail("Redis authentication failed, cannot start application")

redis_client = RedisClient()