from datetime import datetime
from typing import Annotated

from fastapi import Body
from pydantic import BaseModel, Field

from .interface import RequestSchema, ResponseSchema
from .users import Password, UserModel, Username


class SessionInfo(BaseModel):
    created_at: int = Field(
        ...,
        description='The timestamp when the session was created.',
    )

    user_id: str = Field(
        ...,
        description='The ID of the user associated with the session.',
    )

    client_id: str

    user_agent: str = Field(
        ...,
        description='The user agent string from the client that created the session.',
    )

    ip_address: str = Field(
        ...,
        description='The IP address from which the session was created.',
    )

    last_seen: int = Field(
        ...,
        description='The timestamp when the session was last active.',
    )

    extras: dict[str, str] | None = Field(
        None,
        description='Any additional metadata associated with the session.',
    )


class LoginModel(RequestSchema):
    username: Username
    password: Password


CreatedAt = Annotated[
    datetime,
    Field(
        ..., description='The time the session was created in seconds ( time.tme() )'
    ),
]
ExpiresAt = Annotated[
    datetime,
    Field(..., description='The time the session expires in seconds ( time.tme() )'),
]
IdleTimeout = Annotated[
    datetime,
    Field(..., description='The time the session expires due to inactivity in seconds'),
]


class SessionResponse(ResponseSchema):
    """The response after a successful login that contains the signed API key and
    the identity of the client
    """

    session_id: str = Field(
        ..., description='the signed API key to be issued to the client'
    )

    created_at: CreatedAt

    expires_at: ExpiresAt

    idle_timeout: IdleTimeout

    user: UserModel = Field(
        ..., description='the identity of the user associated with the user'
    )


class SessionHealth(ResponseSchema):
    expires_at: ExpiresAt
    idle_timeout: IdleTimeout
    created_at: CreatedAt


class LogoutResponse(ResponseSchema):
    message: str = 'Successfully logged out'
    success: bool = True


LoginRequest = Annotated[
    LoginModel,
    Body(
        ...,
        description='The request body to login; only username and password are allowed',
    ),
]
