


from typing import Annotated

from pydantic import Field

from range_monitor.schema import PageParams, PageSchema, RequestSchema, ResponseSchema
from range_monitor.users.roles import UserRoles
from range_monitor.users.sessions.schema import SessionClaim

Role = Annotated[
    UserRoles,
    Field(description='The name of the role')
]


Username = Annotated[
    str,
    Field(
        description='The username of the user',
        max_length=128,
        min_length=3,
        pattern=r'^[a-zA-Z0-9_.-]+$',
    ),
]

Password = Annotated[
    str,
    Field(
        description='The password of the user',
        max_length=255,
    )
]

UserID = Annotated[
    str,
    Field(description='The unique identifier of the user')
]


class UserLoginRequest(RequestSchema):
    username: Username = Field(...)
    password: Password = Field(...)

class LoginResponse(ResponseSchema):
    session: SessionClaim = Field(...)
    role: Role = Field(...)
    username: Username = Field(...)
    user_id: UserID = Field(...)


class UserSchema(RequestSchema):
    id: UserID = Field(...)
    username: Username = Field(...)
    role: Role = Field(...)


class UserUpdateSelfBody(ResponseSchema):
    username: Username | None = None
    password: Password | None = None


class AdminUpdateUserBody(ResponseSchema):
    username: Username | None = None
    password: Password | None = None
    role: Role | None = None


class CreateUserBody(ResponseSchema):
    username: Username = Field(...)
    password: Password
    role: Role


class UserQuery(PageParams):
    role: Role | None = None


class UserListResponse(PageSchema):
    data: list[UserSchema]

