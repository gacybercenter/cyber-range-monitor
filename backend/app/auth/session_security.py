

from typing import Optional
from fastapi import Request, Response
from fastapi.security.base import SecurityBase

from app.auth.errors import HTTPInvalidOrExpiredSession
from .schemas import ClientIdentity, SessionData
from . import session_manager


class SessionIdAuthority(SecurityBase):
    '''A custom class based security dependency that checks the validity of the session
    and resolves the "Identity" of the associated session to server side "SessionData" 
    for OpenAPI documentation.

    The SessionIdentitySecurity then checks if the identity of the client has changed since the 
    session id was issued, if so the session is terminated and a 401 is returned.
    '''

    def __init__(self) -> None:
        self.scheme_name = 'SessionIdAuthority'
        self.model: dict = {
            'name': 'SessionIdAuthority',
            'in': 'cookie',
            'description': 'The session id issued by the server'
        }

    async def __call__(
        self,
        request: Request,
        response: Response
    ) -> SessionData:
        '''The method that is called when the dependency is resolved

        Arguments:
            request {Request} -- The request object

        Returns:
            SessionData -- The session data associated with the session id
        '''
        signed_id = await session_manager.get_session_cookie(request)
        if not signed_id:
            raise HTTPInvalidOrExpiredSession()
        client_identity = await ClientIdentity.create(request)
        session_data = await session_manager.get_session(signed_id, client_identity)
        if not session_data:
            await session_manager.revoke_session(signed_id, response)
            raise HTTPInvalidOrExpiredSession()
        return session_data


