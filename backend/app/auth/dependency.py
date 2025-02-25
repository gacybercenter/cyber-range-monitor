from fastapi import Depends, Request
from typing import Annotated
from .const import SESSION_COOKIE_BEARER
from .schemas import SessionData, ClientIdentity


async def get_client_identity(request: Request) -> ClientIdentity:
    return await ClientIdentity.create(request)

SessionSecurity = Annotated[SessionData, Depends(SESSION_COOKIE_BEARER)]
RequireClientIdentity = Annotated[ClientIdentity, Depends(get_client_identity)]