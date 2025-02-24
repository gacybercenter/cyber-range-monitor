from typing import Dict, Optional
from fastapi import Request, Response

from fastapi.security.base import SecurityBase
from .errors import HTTPInvalidSession
from .schemas import ClientIdentity, SessionData
from .service import SessionService



class SessionAuthority(SecurityBase):
    '''A custom class based security dependency that checks the validity of the session
    and resolves the "Identity" of the associated session to server side "SessionData" 
    for OpenAPI documentation.

    The SessionIdentitySecurity then checks if the identity of the client has changed since the 
    session id was issued, if so the session is terminated and a 401 is returned.
    '''

    def __init__(self, session_cookie: str) -> None:
        self.cookie_name = session_cookie
        self.scheme_name = 'SessionAuthSchema'
        self.session_manager = SessionService()
        self.model: Dict = {
            'type_': 'Session',
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

        signature = request.cookies.get(self.cookie_name)
        if not signature:
            raise HTTPInvalidSession()

        client_identity = ClientIdentity.create(request)

        session = await self.session_manager.get_session(signature, client_identity)
        if not session:
            await self.revokes(signature, response)
            raise HTTPInvalidSession()
        return session

    async def revokes(self, signature: Optional[str], response: Response) -> None:
        if signature:
            await self.session_manager.end_session(signature)
        response.delete_cookie(self.cookie_name)

    
    async def issue_session(self, session_data: SessionData) -> str:
        '''Issues a session to the client and returns the signed session id

        Arguments:
            session_data {SessionData} -- the session data to issue

        Returns:
            str -- the signed session id
        '''
        return await self.session_manager.create(session_data)