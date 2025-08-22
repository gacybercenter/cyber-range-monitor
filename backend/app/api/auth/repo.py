from datetime import UTC, datetime
from typing import TypeVar

import redis.asyncio as aioredis
from pydantic import BaseModel

from .schema import SessionPayload

S = TypeVar('S', bound=BaseModel)


def k_session(session_id: str) -> str:
    return f'auth:{session_id}'

def k_user_session(user_id: str) -> str:
    return f'auth:user_sessions:{user_id}'

class SessionRepo:
    def __init__(self, redis: aioredis.Redis) -> None:
        self.redis_client: aioredis.Redis = redis

    async def save(
        self,
        payload: SessionPayload,
        *,
        ttl: int,
    ) -> None:
        '''
        Saves a session payload to Redis.

        Parameters
        ----------
        payload : SessionPayload
        ttl : int
        '''
        session_payload = payload.model_dump()
        sid_key = k_session(payload.session_id)
        uid_key = k_user_session(payload.user_id)
        pipeline = self.redis_client.pipeline(transaction=True)  # type: ignore

        pipeline.hset(
            sid_key,
            mapping=session_payload
        )
        pipeline.expire(sid_key, ttl)
        pipeline.zadd(uid_key, {
            payload.session_id: payload.created_at
        })

        await pipeline.execute()


    async def touch(
        self,
        session_id: str,
        user_id: str,
        *,
        last_seen: int,
        extend_ttl: int | None = None,
    ) -> None:
        """
        Updates the last seen time for the session and user.
        """
        sid_key = k_session(session_id)
        uid_key = k_user_session(user_id)
        pipeline = self.redis_client.pipeline(transaction=True)  # type: ignore
        pipeline.hset(sid_key, mapping={'last_seen': last_seen})
        if extend_ttl:
            pipeline.expire(sid_key, extend_ttl)

        pipeline.zadd(uid_key, {session_id: last_seen})
        await pipeline.execute()

    def try_load_payload(self, raw: dict[str, str]) -> SessionPayload | None:
        try:
            return SessionPayload.model_validate(raw)
        except Exception:
            return None

    async def load(
        self,
        session_id: str,
        *,
        extend_ttl: int | None = None
    ) -> SessionPayload | None:
        '''
        Loads a session payload by session ID.

        Parameters
        ----------
        session_id : str
        extend_ttl : int | None, optional
            _The time in seconds to extend the session by_, by default None

        Returns
        -------
        SessionPayload | None
            _The payload if successfully loaded_
        '''
        sid_key = k_session(session_id)

        session_dict = await self.redis_client.hgetall(sid_key)  # type: ignore
        if not session_dict:
            return None

        if not (payload := self.try_load_payload(session_dict)):
            return None

        last_seen = int(datetime.now(UTC).timestamp())
        await self.touch(
            session_id,
            payload.user_id,
            last_seen=last_seen,
            extend_ttl=extend_ttl,
        )

    async def list_sessions(
        self,
        user_id: str,
        *,
        limit: int = 50,
    ) -> list[SessionPayload]:
        """
        Sessions are returned most-recent-first based on ZSET order.
        Removes any dangling ZSET members that no longer have a backing hash.
        """
        z_key = k_user_session(user_id)

        sids = await self.redis_client.zrevrange(  # type: ignore
            z_key,
            0,
            limit - 1
        )
        if not sids:
            return []


        pipe = self.redis_client.pipeline(transaction=False)
        for sid in sids:
            redis_key = k_session(sid)
            pipe.hgetall(redis_key)

        rows = await pipe.execute()
        results: list[SessionPayload] = []
        for row in rows:
            if not row:
                continue
            if not (payload := self.try_load_payload(row)):
                await self.redis_client.zrem(z_key, sid)
                continue

            results.append(payload)

        return results

    async def remove_all(self, user_id: str) -> None:
        """
        Removes all sessions for a user.
        """
        z_key = k_user_session(user_id)
        sids = await self.redis_client.zrange(z_key, 0, -1)
        if not sids:
            return
        pipe = self.redis_client.pipeline(transaction=True)

        for sid in sids:
            pipe.delete(k_session(sid))

        pipe.delete(z_key)

        await pipe.execute()

    async def remove(self, session_id: str) -> None:
        """
        Removes a single session by ID.
        """
        sid_key = k_session(session_id)
        await self.redis_client.delete(sid_key)


