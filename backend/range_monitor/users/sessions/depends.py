

from typing import Annotated, Final

from fastapi import Depends

from range_monitor.depends import RedisDep, SignatureDep
from range_monitor.users.sessions.backend import SessionBackend
from range_monitor.users.sessions.security import HTTPSessionBearer
from range_monitor.users.sessions.service import SessionService


async def get_session_backend(redis: RedisDep) -> SessionBackend:
    return SessionBackend(client=redis)


async def get_session_service(
    signatures: SignatureDep,
    sessions: SessionBackend = Depends(get_session_backend),
) -> SessionService:
    return SessionService(
        signatures=signatures,
        sessions=sessions,
    )

SessionBackendDep = Annotated[SessionBackend, Depends(get_session_backend)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
SessionSecurity: Final[HTTPSessionBearer] = HTTPSessionBearer()
