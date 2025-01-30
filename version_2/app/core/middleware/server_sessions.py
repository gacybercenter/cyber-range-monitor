from typing import Callable, Awaitable, Dict, Any, Optional
import secrets
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
import aioredis
import json
from cryptography.fernet import Fernet
from app.core.config import settings
from redis.asyncio import Redis

fernet = Fernet(settings.SESSION_ENCRYPTION_KEY.encode())


class ServerSideSessionMiddleware(BaseHTTPMiddleware):
    '''_summary_
    Custom Middleware to handle server-side sessions using Redis and Fernet. 
    Fernet encrypts the session payload and handles the encryption.

    The server assigns a session id to the client and stores the session data in Redis
    till the session expires. Although the client has the session id stored as a cookie,
    it cannot decrypt the session data without the servers Session Encryption Key. 

    Arguments:
        BaseHTTPMiddleware 
    '''

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.redis_client: Redis = aioredis.from_url(
            settings.redis_url,
            decode_responses=True,
            encoding="utf-8"
        )

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        client_session_id = request.cookies.get(settings.SESSION_COOKIE)
        session_data = {}
        if not client_session_id:
            client_session_id = secrets.token_urlsafe(32)
            await self._encrypt_payload(client_session_id)
        else:
            encrypted_payload = await self.redis_client.get(client_session_id)
            if not encrypted_payload:
                await self._encrypt_payload(client_session_id)
            else:
                session_data = await self._try_decrypt(client_session_id, encrypted_payload)

        request.state.session = session_data

        response: Response = await call_next(request)

        encoded_session = json.dumps(request.state.session).encode()
        encrypted_data = fernet.encrypt(encoded_session).decode()
        await self.redis_client.set(
            client_session_id,
            encrypted_data,
            ex=settings.SESSION_LIFETIME
        )

        response.set_cookie(
            key=settings.SESSION_COOKIE,
            value=client_session_id,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            secure=settings.SESSION_COOKIE_SECURE,
            max_age=settings.SESSION_LIFETIME,
            samesite=settings.SESSION_COOKIE_SAMESITE,  # type: ignore
            path='/'
        )

        return response

    async def _try_decrypt(self, client_session_id: str, encrypted_payload: str) -> dict:
        try:
            decrypted = fernet.decrypt(encrypted_payload.encode()).decode()
            return json.loads(decrypted)
        except Exception:
            await self._encrypt_payload(client_session_id)
            return {}

    async def _encrypt_payload(
        self,
        client_session_id: str,
        payload: Optional[dict] = {}
    ) -> None:
        encrypted_payload = fernet.encrypt(json.dumps(payload).encode())
        await self.redis_client.set(
            client_session_id,
            encrypted_payload,
            ex=settings.SESSION_LIFETIME
        )
