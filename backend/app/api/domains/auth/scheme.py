from app.infrastructure.security.session_id import (
    SessionID,
    HTTPSessionIDBearer,
    SessionBearerOptions,
)
from .settings import auth_settings
from fastapi import Depends, Request, Security

SessionBearer: HTTPSessionIDBearer = HTTPSessionIDBearer(
    SessionBearerOptions(
        header_name=auth_settings.header_name,
        unauthorized_msg='Session ID is required',
    )
)


async def session_id_required(id: SessionID = Security(SessionBearer)) -> SessionID:
    return id

