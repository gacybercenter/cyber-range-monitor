from typing import Dict
from fastapi import Depends, HTTPException, Request, status
from fastapi.security.base import SecurityBase

from app.core.config import running_config
from app.common.errors import HTTPInvalidSession
from app.schemas.session_schema import SessionData
from app.services.session_service import get_session_service, SessionService
from .models import ClientIdentity, InboundSession


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
        self.scheme_name = 'SessionIdentityAuth'
        self.model: Dict = {
            'type_': 'http',
            'description': 'Stateless session ids issued by the server stored in the client Cookies used to authorize users',
        }

    async def __call__(
        self,
        session_service: SessionService = Depends(get_session_service),
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

        session = session_service.get_session(auth_schema.signature)
        if not session:
            raise HTTPInvalidSession()

        if not session.trusts_client(auth_schema.client):
            session_service.end_session(auth_schema.signature)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Your session has been terminated due to a possible security risk'
            )

        return session
