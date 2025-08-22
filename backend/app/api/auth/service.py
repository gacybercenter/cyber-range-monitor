import secrets
from datetime import UTC, datetime

from app.api.users.schema import UserAuthSchema
from app.core import settings
from app.security import signatures

from .repo import SessionRepo
from .schema import LoginResponseSchema, SessionPayload


def utcnow() -> int:
    return int(datetime.now(tz=UTC).timestamp())


def stamped(utc: int) -> datetime:
    return datetime.fromtimestamp(utc, tz=UTC)


def make_sid() -> str:
    return secrets.token_urlsafe(16)

def _get_auth_settings():
    return settings.get_adapter_settings().sessions


def calc_max_age(created_at: int) -> int:
    return created_at + _get_auth_settings().max_age



def max_age_reached(created_at: int) -> bool:
    return utcnow() > calc_max_age(created_at)

async def create_session(
    user_auth: UserAuthSchema,
    ip_address: str,
    user_agent: str,
    session_repo: SessionRepo
) -> LoginResponseSchema:

    session_id = make_sid()
    created_at = utcnow()

    max_age_at = calc_max_age(created_at)

    payload = SessionPayload(
        session_id=session_id,
        user_id=str(user_auth.id),
        created_at=created_at,
        ip_address=ip_address,
        user_agent=user_agent,
        max_age_at=max_age_at,
    )

    signed_sid = signatures.sign_str(session_id)
    idle_timeout = _get_auth_settings().idle_timeout

    await session_repo.save(
        payload,
        ttl=idle_timeout,
    )

    return LoginResponseSchema(
        created_at=stamped(created_at),
        max_age_at=stamped(max_age_at),
        session_id=signed_sid,
        user_id=user_auth.id,
        role_name=user_auth.role
    )

async def load_session(
    signed_session_id: str,
    session_repo: SessionRepo
) -> SessionPayload | None:
    session_id = signatures.load_signed_str(
        signed_session_id,
        max_age=_get_auth_settings().max_age
    )
    if not session_id:
        return None

    payload = await session_repo.load(
        session_id,
        extend_ttl=_get_auth_settings().idle_timeout
    )

    if not payload or max_age_reached(payload.created_at):
        return None

    return payload


async def revoke_session(signed_session_id: str, session_repo: SessionRepo) -> None:
    session_id = signatures.load_signed_str(signed_session_id)
    if not session_id:
        return

    await session_repo.remove(session_id)

