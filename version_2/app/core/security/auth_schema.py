from typing import Dict, Annotated
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security.base import SecurityBase
from app.core.config import running_config
from app.common.errors import (
    HTTPForbidden,
    HTTPInvalidSession,
    HTTPNotFound,
    HTTPUnauthorized
)
from app.core.db import get_db
from app.services.auth_service import AuthService
from app.services.security import SessionIdentity
from app.schemas.session_schema import SessionData
from .models import ClientIdentity, InboundSession
from app.models.user import User, Role


settings = running_config()


async def get_session_schema(request: Request) -> InboundSession:
    '''_summary_
    Resolves the inbound request to a protected route to an 
    'InboundSession' which contains the session id and a fingerprint
    of the client's identity.
    Arguments:
        request {Request} -- _description_

    Raises:
        HTTPInvalidSession: _description_

    Returns:
        InboundSession -- _description_
    '''
    signature = request.cookies.get(settings.SESSION_COOKIE)
    if not signature:
        raise HTTPInvalidSession()
    client_identity = await ClientIdentity.create(request)
    return InboundSession(
        signature=signature,
        client=client_identity
    )


class SessionAuthSchema(SecurityBase):
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
        self.model: Dict = {
            'type_': 'http',
            'description': 'Stateless session ids issued by the server stored in the client Cookies used to authorize users',
        }

    async def __call__(
        self,
        auth_schema: InboundSession = Depends(get_session_schema)
    ) -> SessionData:
        '''_summary_
        Gets the client identity and session id from the request and 
        once the validity of the session and identity of the client. Guarntees
        authorization of the client but not of the User which may not exist.

        Keyword Arguments:
            session_id {_type_} -- (default: {Depends(require_session_id)})
            client_identity {_type_} -- (default: {Depends(require_fingerprint)})
        Raises:
            HTTPException: 401, the server does not trust the clients identity or 
            the session has expired 
        Returns:
            SessionData 
        '''
        session_identity = SessionIdentity()
        session = session_identity.get_session(auth_schema.signature)
        if not session:
            raise HTTPInvalidSession()

        if not session.trusts_client(auth_schema.client):
            session_identity.end_session(auth_schema.signature)
            raise HTTPInvalidSession(
                'Your session has been terminated due to a possible security risk')

        return session


AuthSchema = SessionAuthSchema()


async def get_current_user(
    session_auth: SessionData = Depends(AuthSchema),
    db: AsyncSession = Depends(get_db)
) -> User:
    '''_summary_
    Gets the current user from the associated session from the Users table

    Keyword Arguments:
        session_data {SessionData} --  {Depends(SessionAuthSchema())})
        db {AsyncSession} -- _description_ (default: {Depends(get_db)})

    Raises:
        HTTPException: 404 if the user is not found

    Returns:
        User
    '''
    auth = AuthService()
    existing_user = await auth.get_username(session_auth.username, db)
    if not existing_user:
        raise HTTPNotFound('User')

    mapped_user = session_auth.client_identity.mapped_user

    if mapped_user != 'Unknown' and mapped_user != existing_user.username:
        raise HTTPUnauthorized(
            'Untrusted session identity'
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
