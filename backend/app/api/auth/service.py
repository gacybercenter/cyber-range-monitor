import time
from datetime import UTC, datetime

import redis.asyncio as aioredis

from api.http_exceptions import HTTPForbidden
from app.api.schemas.auth import SessionInfo, SessionResponse
from app.api.schemas.users import UserModel
from .session import SessionPayload

def utcnow() -> int:
    return int(time.time())


def stamped(utc: int) -> datetime:
    return datetime.fromtimestamp(utc, tz=UTC)


def create_payload(
    user: UserModel,
    session_id: str,
    scopes: list[str] | None = None,
) -> SessionPayload: