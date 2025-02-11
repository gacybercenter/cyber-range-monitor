from typing import Dict, Annotated, Optional
from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security.base import SecurityBase
from app.config import running_config
from app.common.errors import (
    HTTPForbidden,
    HTTPInvalidSession,
    HTTPNotFound,
    HTTPUnauthorized
)
from app.db import get_db
from app.services.auth.auth_service import AuthService
from app.services.auth import SessionService
from app.schemas.session_schema import SessionData
from .models import ClientIdentity
from app.models.enums import Role
from app.models.user import User

settings = running_config()


async def get_client_identity(request: Request) -> ClientIdentity:
    return await ClientIdentity.create(request)

class SessionAuthority(SecurityBase):
    '''_summary_
    A custom class based security dependency that checks the validity of the session
    and resolves the "Identity" of the associated session to server side "SessionData" 
    for OpenAPI documentation.

    The SessionIdentitySecurity then checks if the identity of the client has changed since the 
    session id was issued, if so the session is terminated and a 401 is returned.
    '''

    def __init__(self) -> None:
        self.cookie_name = settings.SESSION_COOKIE
        self.scheme_name = 'SessionAuthSchema'
        self.session_manager = SessionService()
        self.model: Dict = {
            'type_': 'http',
            'description': 'Stateless session ids issued by the server stored in the client Cookies used to authorize users',
        }

    async def __call__(
        self,
        request: Request,
        response: Response
    ) -> SessionData:
        '''Gets the client identity and session id from the request and 
        once the validity of the session and identity of the client. Guarntees
        authorization of the client but not of the User which may not exist.

        Keyword Arguments:
            session_id {_type_} -- (default: {Depends(require_session_id)})
            client_identity {_type_} -- (default: {Depends(require_fingerprint)})
        Raises:
            HTTPerroreption: 401, the server does not trust the clients identity or 
            the session has expired 
        Returns:
            SessionData 
        '''

        signature = request.cookies.get(settings.SESSION_COOKIE)
        if not signature:
            raise HTTPInvalidSession()

        client_identity = await ClientIdentity.create(request)

        session = self.session_manager.get_session(signature)
        if not session:
            await self.revokes(signature, response)
            raise HTTPInvalidSession()

        if not session.trusts_client(client_identity):
            await self.revokes(signature, response)
            raise HTTPInvalidSession(
                'Your session has been terminated due to a possible security risk'
            )

        return session

    async def revokes(self, signature: Optional[str], response: Response) -> None:
        if signature:
            self.session_manager.end_session(signature)
        response.delete_cookie(settings.SESSION_COOKIE)


SessionAuth = SessionAuthority()


async def get_current_user(
    request: Request,
    response: Response,
    session_auth: SessionData = Depends(SessionAuth),
    db: AsyncSession = Depends(get_db)
) -> User:
    '''_summary_
    Gets the current user from the associated session from the Users table and 
    guarntees that the session is valid and that the client is not impersonating 
    another user.

    Keyword Arguments:
        session_data {SessionData} --  {Depends(SessionAuthSchema())})
        db {AsyncSession} -- _description_ (default: {Depends(get_db)})

    Raises:
        HTTPerroreption: 404 if the user is not found

    Returns:
        User
    '''
    auth = AuthService()
    existing_user = await auth.get_username(session_auth.username, db)

    session_signature = request.cookies.get(settings.SESSION_COOKIE)
    mapped_user = session_auth.client_identity.mapped_user
    if not existing_user:
        await SessionAuth.revokes(session_signature, response)
        raise HTTPInvalidSession(
            'Your session corresponds to a non-existent user, please login again'
        )
    elif mapped_user != 'Unknown' and mapped_user != existing_user.username:
        await SessionAuth.revokes(session_signature, response)
        raise HTTPInvalidSession(
            'Your session is not authorized under your current user.'
        )

    return existing_user


class RoleRequired:
    def __init__(self, min_role: Role = Role.READ_ONLY) -> None:
        self.min_role = min_role

    async def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role < self.min_role:
            raise HTTPForbidden(
                'You lack the required permissions to access this resource'
            )
        return user
