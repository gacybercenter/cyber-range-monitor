import asyncio
from contextlib import asynccontextmanager
from redis.asyncio import Redis


def redis_key(*parts: str) -> str:
    return ':'.join(parts)



class RedisRepository:
    '''
    simple wrapper around a Redis client to be used as a repository
    which will likely be extended in the future with common methods
    '''
    def __init__(self, redis: Redis) -> None:
        self.redis: Redis = redis


class RedisNXLock:

    def __init__(
        self,
        redis: Redis,
        *,
        key: str,
    ) -> None:
        self.redis = redis
        self.key = key

    async def acquire(self, lock_ttl: int = 10) -> bool:
        result = await self.redis.set(
            self.key,
            '1',
            nx=True,
            ex=lock_ttl
        )
        return bool(result)

    async def release(self) -> None:
        await self.redis.delete(self.key)

    async def ttl(self) -> int:
        return await self.redis.ttl(self.key)

    @asynccontextmanager
    async def guard(self, lock_ttl: int = 10):
        while not await self.acquire(lock_ttl=lock_ttl):
            ttl = await self.ttl()
            await asyncio.sleep(max(0.1, ttl or 0))

        try:
            yield
        finally:
            await self.release()
