from typing import Annotated

from fastapi import Security

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .const import HTTP_BEARER_DESCRIPTION

session_id_bearer = HTTPBearer(
    auto_error=False,
    description=HTTP_BEARER_DESCRIPTION
)

SessionIdDep = Annotated[
    HTTPAuthorizationCredentials,
    Security(session_id_bearer)
]
