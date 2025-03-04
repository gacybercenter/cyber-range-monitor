from typing import Annotated

from fastapi import Depends, Request

from .const import SESSION_COOKIE_BEARER
from .schemas import ClientIdentity, SessionData


async def get_client_identity(request: Request) -> ClientIdentity:
    return await ClientIdentity.create(request)


SessionSecurity = Annotated[SessionData, Depends(SESSION_COOKIE_BEARER)]
RequireClientIdentity = Annotated[ClientIdentity, Depends(get_client_identity)]
