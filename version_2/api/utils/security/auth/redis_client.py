import redis.asyncio as redis
from api.config.settings import app_config


class RedisClient:
    client = redis.Redis(
        host=app_config.REDIS_HOST,
        port=app_config.REDIS_PORT,
        decode_responses=True
    )

    @staticmethod
    async def blacklist_token(jti: str, token: str) -> None:
        await RedisClient.client.set(
            f'blacklist:{jti}', token
        )

    @staticmethod
    async def has_blacklisted(jti: str) -> bool:
        return await RedisClient.client.exists(f'blacklist:{jti}')
