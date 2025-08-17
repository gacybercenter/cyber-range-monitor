from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.infrastructure.repos import RedisRepository, RedisPipelineAdapter
from .settings import auth_settings

S = TypeVar('S', bound=BaseModel)


def session_key(key: str) -> str:
    return f'{auth_settings.redis_prefix}:session:{key}'


def user_session_key(user_id: str) -> str:
    return f'{auth_settings.redis_prefix}:{user_id}:session'

class SessionPayloadAdapter(RedisPipelineAdapter):

    def key(self, )


class SessionRepository(RedisRepository, Generic[S]):
    async def store_payload(
        self,
        payload_key: str,
        payload: dict,
        *,
        expires: int,
    ) -> None:
        payload_redis_key = session_key(payload_key)

        pipeline = self.redis_client.pipeline()
        pipeline.hset(payload_redis_key, mapping=payload)
        pipeline.expire(payload_redis_key, expires)
        await pipeline.execute()

    async def load_payload(
        self,
        key: str,
        *,
        payload_model: type[BaseModel],
    ) -> Any | None:
        redis_key = session_key(key)
        data = await self.redis_client.hgetall(redis_key)  # type: ignore

        if not data:
            return None

        try:
            payload = payload_model.model_validate(data)
        except Exception:
            return None

        return payload

    async def exists(self, unsigned_id: str) -> bool:
        redis_key = session_key(unsigned_id)
        exists = await self.redis_client.exists(redis_key)
        return bool(exists)

    async def extend(self, unsigned_id: str, expires: int) -> None:
        redis_key = session_key(unsigned_id)
        await self.redis_client.expire(redis_key, expires)

    async def delete(self, unsigned_id: str) -> None:
        redis_key = session_key(unsigned_id)
        await self.redis_client.delete(redis_key)

    async def get_ttl(self, unsigned_id: str) -> int:
        ttl = await self.redis_client.ttl(session_key(unsigned_id))
        return ttl if ttl >= 0 else 0
