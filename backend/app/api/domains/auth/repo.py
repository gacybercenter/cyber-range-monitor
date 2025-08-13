from typing import Generic, TypeVar

from pydantic import BaseModel

from app.infrastructure.repos.redis_repo import RedisRepository

S = TypeVar('S', bound=BaseModel)


def session_key(key: str) -> str:
    return f'auth:sessions:{key}'


class SessionRepository(RedisRepository, Generic[S]):

    async def store(
        self, unsigned_id: str, session_payload: dict, expires_at: int
    ) -> None:
        redis_key = session_key(unsigned_id)
        pipeline = self.redis_client.pipeline()
        pipeline.hset(redis_key, mapping=session_payload)
        pipeline.expire(redis_key, expires_at)

        await pipeline.execute()

    async def load(
        self,
        unsigned_id: str,
        payload_cls: type[S],
    ) -> S | None:
        redis_key = session_key(unsigned_id)
        data = await self.redis_client.hgetall(redis_key)  # type: ignore

        if not data:
            return None

        try:
            payload = payload_cls.model_validate(data)
        except Exception:
            return None

        return payload

    async def extend(self, unsigned_id: str, expire_secs: int) -> None:
        redis_key = session_key(unsigned_id)
        await self.redis_client.expire(redis_key, expire_secs)

    async def remove(self, unsigned_id: str) -> None:
        redis_key = session_key(unsigned_id)
        await self.redis_client.delete(redis_key)

    async def get_ttl(self, unsigned_id: str) -> int:
        ttl = await self.redis_client.ttl(session_key(unsigned_id))
        return ttl if ttl >= 0 else 0
