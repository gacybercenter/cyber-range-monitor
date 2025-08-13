
import redis.asyncio


class RedisRepository:
    def __init__(self, redis_client: redis.asyncio.Redis) -> None:
        self.redis_client: redis.asyncio.Redis = redis_client

