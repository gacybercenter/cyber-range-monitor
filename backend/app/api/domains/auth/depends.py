from typing import Annotated

from fastapi import Depends, Request, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param

from app.api.schemas.auth import SessionPayload
from app.infrastructure.security.sessions import SessionId

from ..depends import RedisDep
from .repo import SessionRepository
from .service import SessionService


class SessionSecurity(OAuth2PasswordBearer):
    _DESCRIPTION = (
        'Custom implementation of OAuth2PasswordBearer that uses session IDs '
        'instead of access tokens (_so we get token URL in docs_).\n\n'
        'This class is a dependency and as a dependency it simply checks for the '
        'session ID in the request header, removes the signature and returns it.\n\n'
        'It does not raise an exception and is the responsibility of the caller to '
        'handle the absence of the session ID or invalid signatures.'
    )

    def __init__(self) -> None:
        super().__init__(
            tokenUrl='/auth/login',
            auto_error=False,
            description=self._DESCRIPTION,
            scheme_name=self.__class__.__name__,
        )

    async def __call__(self, request: Request) -> SessionId | None:
        """
        Extracts the session ID from the request headers. Does not raise an error
        or check if the session ID is valid or not.
        Parameters
        ----------
        request : Request
            _The request sent by the client_

        Returns
        -------
        SessionId | None
        """
        authorization: str | None = request.headers.get('Authorization')
        if not authorization:
            return None

        scheme, signed_id = get_authorization_scheme_param(authorization)
        if scheme.lower() != 'session':
            return None

        return SessionId.load(signed_id)


session_auth = SessionSecurity()
SessionIdDepends = Security(session_auth)
SessionIdDep = Annotated[SessionId, Depends(SessionIdDepends)]


async def get_session_repo(redis: RedisDep) -> SessionRepository:
    return SessionRepository(redis)


async def get_session_service(redis: RedisDep) -> SessionService:
    return SessionService(redis)


SessionServiceDepends = Depends(get_session_service)
SessionRepositoryDepends = Depends(get_session_repo)

SessionServiceDep = Annotated[SessionService, SessionServiceDepends]
SessionRepositoryDep = Annotated[SessionRepository, SessionRepositoryDepends]


async def session_required(
    request: Request,
    session_id: SessionIdDep,
    session_service: SessionServiceDep,
) -> SessionPayload:
    """
    Dependency to ensure that a session ID is present in the request.
    If not, it returns None, allowing the caller to handle the absence of a session ID.
    """
    fingerprint = request.state.fingerprint
    return await session_service.load_session(
        id=session_id,
        inbound_client=fingerprint,
    )


SessionRequiredDepends = Depends(session_required)
SessionRequiredDep = Annotated[SessionPayload, SessionRequiredDepends]
