from typing import Annotated

from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .const import HTTP_BEARER_DESCRIPTION


class SessionIdBearer(HTTPBearer):
    """Bearer token wrapper for session IDs, checks if the state
    middleware has already set the session ID in the request state.

    """

    def __init__(self) -> None:
        super().__init__(auto_error=False, description=HTTP_BEARER_DESCRIPTION)


session_id_bearer = SessionIdBearer()


SessionIdDep = Annotated[HTTPAuthorizationCredentials, Security(session_id_bearer)]
