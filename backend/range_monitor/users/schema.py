import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field

from range_monitor.auth.schema import TokenClaim
from range_monitor.core.enums import UserRoles
from range_monitor.schema.http import (
    PageModel,
    PydanticMixin,
    RequestBody,
    ResponseModel,
)

SessionID = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier of the session.'
    )
]


JTI = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier for the JWT.',
    )
]
UserID = Annotated[
    uuid.UUID,
    Field(
        ...,
        description='The unique identifier of the user.',
    )
]

Username = Annotated[
    str,
    Field(
        ...,
        description='The username of the user.',
        min_length=3,
        max_length=128,
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
]
Password = Annotated[
    str,
    Field(
        ...,
        description='The password of the user.',
        min_length=3,
        max_length=128,
    )
]
Role = Annotated[
    UserRoles,
    Field(
        ...,
        description='The role of the user.',
    )
]



class LoginRequest(RequestBody):
    username: Username
    password: Password


class TokenResponse(ResponseModel):
    claim: TokenClaim
    user_id: UserID
    username: Username
    role: Role

class InternalUser(PydanticMixin):
    id: UserID
    username: Username
    role: Role
    cver: int
    password_hash: str

class UserSchema(ResponseModel):
    id: UserID
    username: Username
    role: Role
    last_login_at: datetime | None = None


UsernameSearch = Annotated[
    str,
    Field(
        ...,
        description='A search string to filter usernames.',
        min_length=1,
        max_length=128,
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
]

class UserQuery(RequestBody):
    with_role: Role | None = None
    search: UsernameSearch | None = None
    logged_in_after: datetime | None = None
    created_by: Username | None = None


class UserPage(PageModel[UserSchema]):
    data: list[UserSchema]

class UserCreateBody(RequestBody):
    username: Username
    password: Password
    role: Role

class GuestCreateBody(RequestBody):
    username: Username
    password: Password


class UserPatchBody(RequestBody):
    username: Username | None = None
    password: Password | None = None
    role: Role | None = None

class TokenRequestBody(RequestBody):
    refresh_token: str = Field(
        ...,
        description='The refresh token used to obtain a new access token.'
    )
    access_token: str = Field(
        ...,
        description=(
            'The current access token, if available. This is used to verify '
            'the session and ensure the refresh token is valid.'
        )
    )


class UserPatchProfile(RequestBody):
    username: Username | None = None
    password: Password | None = None


class TokenUser(ResponseModel):
    user_id: UserID
    username: Username
    cver: int
    role: Role


class TokenDetails(ResponseModel):
    user: TokenUser
    issued_at: datetime
    expires_at: datetime
    time_to_live: int

class GuestAccount(ResponseModel):
    id: UserID
    username: Username


class UserGuestList(ResponseModel):
    guests: list[GuestAccount]
    total: int