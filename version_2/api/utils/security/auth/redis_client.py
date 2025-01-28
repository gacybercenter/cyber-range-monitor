import redis.asyncio as redis
from api.config import settings


class RedisClient:
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
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

