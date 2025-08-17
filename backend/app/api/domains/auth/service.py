import time
from datetime import datetime

import redis.asyncio as aioredis
from api.exceptions.http import HTTPForbidden, HTTPUnauthorized
from fastapi import HTTPException

from app.api.schemas.auth import SessionPayload, SessionResponse
from app.api.schemas.users import UserModel
from app.infrastructure.security.fingerprint import (
    RequestFingerprint,
    check_fingerprint,
    hash_fingerprint,
)
from app.infrastructure.security.sessions import SessionId, utcnow

from .repo import SessionRepository
from .settings import auth_settings


def has_expired(start_time: float, duration: float) -> bool:
    """Calculates the time remaining before the key expires"""
    elapsed = time.time() - start_time
    remaining = duration - elapsed
    return remaining <= 0


def get_idle_expiration(created_at: float) -> int:
    return int(created_at + auth_settings.idle_timeout)


def get_max_expiration(created_at: float) -> int:
    return int(created_at + auth_settings.session_max_age)


class SessionService(RedisMixin):
    """The SessionService is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self._repo: SessionRepository = SessionRepository[SessionPayload](redis)

    def create_session_id(self) -> SessionId:
        return SessionId.create()

    async def create_session(
        self,
        id: SessionId,
        auth: UserModel,
        fingerprint: RequestFingerprint,
    ) -> SessionResponse:
        payload = SessionPayload(
            user_id=auth.id,
            created_at=utcnow(),
            fingerprint_hash=hash_fingerprint(fingerprint),
        )
        payload_dump = payload.model_dump()
        if not id.unsigned_id:
            raise ValueError('Session ID must be unsigned')

        await self._repo.store(
            id.unsigned_id,
            payload_dump,
            get_idle_expiration(payload.created_at),
        )
        return SessionResponse(
            session_id=id.signed_id,
            user=auth,
            created_at=datetime.fromtimestamp(payload.created_at),
            expires_at=datetime.fromtimestamp(get_max_expiration(payload.created_at)),
            idle_timeout=datetime.fromtimestamp(
                get_idle_expiration(payload.created_at)
            ),
        )

    async def parse_session_id(self, id: SessionId | None) -> SessionPayload:
        if id is None:
            raise HTTPUnauthorized('You must be authenticated to access this resource')

        if not id.unsigned_id:
            raise HTTPUnauthorized('You must be authenticated to access this resource')
        payload = await self._repo.load(
            id.unsigned_id,
            payload_cls=SessionPayload,
        )
        if not payload:
            raise HTTPForbidden('The session is invalid or has expired')
        return payload

    async def _validate_payload(
        self,
        payload: SessionPayload,
        id: SessionId,
        inbound_client: RequestFingerprint,
    ) -> HTTPException | None:
        """Validates the session and returns its health status."""
        if payload.has_expired(auth_settings.session_max_age):
            await self._repo.remove(id.unsigned_id)  # type: ignore[call-arg]
            return HTTPForbidden('This session has expired, please login again')

        if not check_fingerprint(inbound_client, payload.fingerprint_hash):
            return HTTPForbidden('The session is invalid or has expired')

        return None

    async def load_session(
        self,
        *,
        id: SessionId | None,
        inbound_client: RequestFingerprint,
    ) -> SessionPayload:
        payload = await self.parse_session_id(id)
        validation_error = await self._validate_payload(payload, id, inbound_client)  # type: ignore[call-arg]
        if validation_error:
            raise validation_error

        await self._repo.extend(
            id.unsigned_id,  # type: ignore[call-arg]
            get_idle_expiration(payload.created_at),
        )

        return payload

    async def revoke_session(self, session_id: str) -> None:
        await self._repo.remove(session_id)
