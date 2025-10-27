import logging

from server.db import redis, sql
from server.exceptions import StartupError
from server.external.api_clients import ApiClientOptions, api_client_pool
from server.external.auth_flows import GuacamoleToken, SaltstackAuthToken

logger = logging.getLogger(__name__)


async def on_startup() -> None:
    logger.info('ASGI startup: Pinging SQLite & Redis.')

    if not await sql.is_db_reachable():
        logger.critical('SQLite database is not reachable.')
        raise StartupError('SQLite database is not reachable.')

    if not await redis.ping_redis():
        logger.critical('Redis server is not reachable.')
        raise StartupError('Redis server is not reachable.')

    base_headers = {'User-Agent': 'range-monitor/1.0'}

    api_client_pool.register({
        'guacamole': ApiClientOptions(
            name='guacamole',
            auth=GuacamoleToken,
            headers=base_headers,
        ),
        'saltstack': ApiClientOptions(
            name='saltstack',
            auth=SaltstackAuthToken,
            headers=base_headers,
        ),
    })


async def on_shutdown() -> None:
    logger.info('ASGI shutdown: Performing cleanup tasks.')
    await sql.dispose_db()
    await redis.disconnect_redis()
    await api_client_pool.adispose()
    logger.info('Cleanup tasks completed.')
