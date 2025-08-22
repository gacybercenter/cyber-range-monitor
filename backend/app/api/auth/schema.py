


from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.core.schema import PydanticSchema


class SessionPayload(PydanticSchema):
    user_id: str
    session_id: str
    created_at: int
    last_seen: int = -1
    max_age_at: int
    ip_address: str | None = None
    user_agent: str | None = None



LoginUsername = Annotated[
    str,
    Field(
        ...,
        description='The username of the user logging in.',
        min_length=3,
        max_length=255,
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
]
LoginPassword = Annotated[
    str,
    Field(
        ...,
        description='The password of the user logging in.',
        min_length=8,
    )
]

CreatedAt = Annotated[
    datetime, Field(description='The timestamp when the session was created.')
]
MaxAgeAt = Annotated[
    datetime,
    Field(description='The maximum age of the session, after which it will expire.'),
]

class LoginSchema(PydanticSchema):
    username: LoginUsername
    password: LoginPassword




class LoginResponseSchema(PydanticSchema):
    created_at: CreatedAt
    max_age_at: MaxAgeAt
    session_id: str
    user_id: UUID
    role_name: str



