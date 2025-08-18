import time
from datetime import UTC, datetime

import redis.asyncio as aioredis

from app.api.exceptions.http import HTTPForbidden
from app.api.schemas.auth import SessionInfo, SessionResponse
from app.api.schemas.users import UserModel
from app.infrastructure.security.fingerprint import RequestFingerprinter, RequestInfo
from app.infrastructure.security.signatures import IdSignerService

from .repo import SessionRepository
from .settings import auth_settings


def utcnow() -> int:
    return int(time.time())


def stamped(utc: int) -> datetime:
    return datetime.fromtimestamp(utc, tz=UTC)


class SessionService:
    """The SessionService is responsible for creating, storing, and retrieving API Keys
    from the redis store. The API Key Provider is also responsible for checking if the API Key has
    reached the maximum lifetime and revoking the API Key if it has been hijacked.

    Everytime a key is retrieved and is valid the lifetime or time before it expires is extended in redis
    """

    def __init__(self, redis: aioredis.Redis) -> None:
        self._repo: SessionRepository = SessionRepository(redis)

    def new_session_info(
        self,
        request_info: RequestInfo,
        user: UserModel,
        created_at: int,
    ) -> SessionInfo:
        fingerprinter = RequestFingerprinter()
        client_id = fingerprinter.hash_request(request_info)
        return SessionInfo(
            user_id=user.id,
            created_at=created_at,
            ip_address=request_info.ip,
            last_seen=created_at,
            user_agent=request_info.user_agent.id,
            client_id=client_id,
            extras=None
        )

    async def create_session(
        self,
        auth: UserModel,
        fingerprint: RequestInfo,
    ) -> SessionResponse:
        creation = utcnow()
        id_signer = IdSignerService()
        unsigned_id = id_signer.generate_unsigned_id()
        payload = self.new_session_info(
            request_info=fingerprint,
            user=auth,
            created_at=creation,
        )

        idle_timeout = creation + auth_settings.idle_timeout
        max_age = creation + auth_settings.max_age
        await self._repo.store_session(
            session_id=unsigned_id,
            payload=payload,
            ttl=idle_timeout
        )
        signed_id = id_signer.sign_id(unsigned_id)
        return SessionResponse(
            session_id=signed_id,
            user=auth,
            created_at=stamped(creation),
            expires_at=stamped(max_age),
            idle_timeout=stamped(idle_timeout),
        )

    def invalid_session(self) -> HTTPForbidden:
        """Returns a 403 Forbidden error for invalid or expired sessions."""
        return HTTPForbidden(
            'Invalid or expired session, please log in again.'
        )

    async def get_session(
        self,
        *,
        unsigned_id: str | None,
        client: RequestInfo
    ) -> SessionInfo:
        if not unsigned_id:
            raise self.invalid_session()

        session = await self._repo.load_session(unsigned_id)
        if not session:
            raise self.invalid_session()

        fingerprinter = RequestFingerprinter()
        if not fingerprinter.check_fingerprint(
            fingerprint=client,
            stored_hash=session.client_id
        ):
            await self._repo.delete(unsigned_id)
            raise self.invalid_session()


        await self._repo.extend(unsigned_id, auth_settings.idle_timeout)
        return session

    async def remove_session(self, session_id: str | None) -> None:
        if not session_id:
            return
        await self._repo.delete(session_id)

