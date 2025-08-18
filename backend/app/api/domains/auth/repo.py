import json
import time
from typing import Any, TypeVar

from pydantic import BaseModel

from app.api.schemas.auth import SessionInfo
from app.infrastructure.repos import RedisRepository

from .settings import auth_settings

S = TypeVar('S', bound=BaseModel)


def session_key(key: str) -> str:
    return f'{auth_settings.redis_prefix}:session:{key}'


def user_session_key(user_id: str) -> str:
    return f'{auth_settings.redis_prefix}:{user_id}:session'


class SessionRepository(RedisRepository):
    async def store_session(
        self,
        session_id: str,
        payload: SessionInfo,
        *,
        ttl: int,
    ) -> None:
        sid_key = session_key(session_id)
        uid_key = user_session_key(payload.user_id)

        session_payload = payload.model_dump(exclude_none=True)
        if extras := session_payload.get('extras'):
            session_payload['extras'] = json.dumps(extras, separators=(',', ':'))

        async with self.redis_client.pipeline(transaction=True) as pipeline:  # type: ignore
            pipeline.hset(sid_key, mapping=session_payload)
            pipeline.expire(sid_key, ttl)
            pipeline.zadd(uid_key, {session_id: payload.created_at})
            await pipeline.execute()

    def try_load_session(self, data: dict[str, Any]) -> SessionInfo | None:
        if 'extras' in data and data['extras']:
            try:
                data['extras'] = json.loads(data['extras'])
            except json.JSONDecodeError:
                data['extras'] = None
        try:
            return SessionInfo.model_validate(data)
        except Exception:
            return None

    async def load_session(
        self,
        session_id: str,
    ) -> SessionInfo | None:
        sid_key = session_key(session_id)
        raw = await self.redis_client.hgetall(sid_key)  # type: ignore
        if not raw:
            return None

        parsed = self.try_load_session(raw)
        if parsed is None:
            return None

        now = int(time.time())
        uid_key = user_session_key(parsed.user_id)

        async with self.redis_client.pipeline(transaction=True) as pipe:  # type: ignore
            pipe.hset(sid_key, mapping={'last_seen': now})
            pipe.zadd(uid_key, {session_id: now})
            await pipe.execute()

        parsed.last_seen = now
        return parsed

    async def list_user_sessions(
        self,
        user_id: str,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> list[SessionInfo]:
        """
        Sessions are returned most-recent-first based on ZSET order.
        Removes any dangling ZSET members that no longer have a backing hash.
        """
        z_key = user_session_key(user_id)

        sids = await self.redis_client.zrevrange(  # type: ignore
            z_key, offset, offset + limit - 1
        )
        if not sids:
            return []

        results: list[SessionInfo] = []
        to_prune: list[str] = []

        async with self.redis_client.pipeline(transaction=False) as pipe:  # type: ignore
            for sid in sids:
                pipe.hgetall(session_key(sid))
            hashes = await pipe.execute()

        for sid, h in zip(sids, hashes):
            if not h:
                to_prune.append(sid)
                continue
            info = self.try_load_session(h)
            if info:
                results.append(info)
            else:
                to_prune.append(sid)

        if to_prune:
            await self.redis_client.zrem(z_key, *to_prune)  # type: ignore

        return results

    async def user_has_session(self, user_id: str) -> bool:
        z_key = user_session_key(user_id)
        count = await self.redis_client.zcard(z_key)
        return count > 0

    async def exists(self, unsigned_id: str) -> bool:
        redis_key = session_key(unsigned_id)
        exists = await self.redis_client.exists(redis_key)
        return bool(exists)

    async def extend(self, unsigned_id: str, expires: int) -> None:
        redis_key = session_key(unsigned_id)
        await self.redis_client.expire(redis_key, expires)

    async def delete(self, unsigned_id: str) -> None:
        redis_key = session_key(unsigned_id)
        existing_session = await self.redis_client.hgetall(redis_key)  # type: ignore
        if not existing_session:
            return None
        user_id = existing_session.get('user_id')
        if user_id:
            user_key = user_session_key(user_id)
            await self.redis_client.zrem(user_key, unsigned_id)
        await self.redis_client.delete(redis_key)

    async def get_ttl(self, unsigned_id: str) -> int:
        ttl = await self.redis_client.ttl(session_key(unsigned_id))
        return ttl if ttl >= 0 else 0
