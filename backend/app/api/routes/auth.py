import logging

from fastapi import APIRouter, Request, status

from ..domains.depends import SessionIdDep, SessionServiceDep, UserServiceDep
from ..exceptions.http import HTTPForbidden
from ..openapi_extra import HTTPError
from ..schemas.auth import (
    LoginRequest,
    LogoutResponse,
    SessionResponse,
)

auth_logger = logging.getLogger(__name__)


auth_router = APIRouter()


@auth_router.post(
    '/login',
    response_model=SessionResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: HTTPError('Invalid credentials'),
    },
)
async def login(
    request: Request,
    credentials: LoginRequest,
    session_service: SessionServiceDep,
    user_service: UserServiceDep,
) -> SessionResponse:
    verified_user = await user_service.authenticate(
        username=credentials.username, plain_password=credentials.password
    )
    id = session_service.create_session_id()
    return await session_service.create_session(
        id=id,
        auth=verified_user,
        fingerprint=request.state.fingerprint,
    )


@auth_router.post(
    '/logout',
    response_model=LogoutResponse,
    responses={
        status.HTTP_403_FORBIDDEN: HTTPError('Invalid or expired session'),
        status.HTTP_401_UNAUTHORIZED: HTTPError('No session ID provided'),
    },
)
async def logout(
    session_id: SessionIdDep, session_service: SessionServiceDep
) -> LogoutResponse:
    if not session_id or not session_id.signed_id:
        raise HTTPForbidden('Invalid or expired Session')
    try:
        await session_service.revoke_session(session_id.signed_id)
    except Exception:
        pass
    return LogoutResponse()
