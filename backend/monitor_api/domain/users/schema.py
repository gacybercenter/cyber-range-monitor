


from typing import Annotated
from uuid import UUID

from pydantic import Field

from monitor_api.core.schema import PydanticSchema

RoleName = Annotated[
    str,
    Field(
        description='The name of the role',
        max_length=64,
    ),
]
RoleDescription = Annotated[
    str,
    Field(
        description='A brief description of the role',
        max_length=255,
    ),
]

RoleID = Annotated[
    UUID,
    Field(description='The unique identifier of the role')
]

RoleLevel = Annotated[
    int,
    Field(description='The level of the role, higher means more privileges', ge=0),
]
RoleScopes = Annotated[
    list[str],
    Field(description='A list of scopes associated with the role')
]


Username = Annotated[
    str,
    Field(
        description='The username of the user',
        max_length=255,
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
    UUID,
    Field(description='The unique identifier of the user')
]

class RoleSchema(PydanticSchema):
    id: RoleID
    name: RoleName
    description: RoleDescription
    scopes: RoleScopes

class CreateRoleSchema(PydanticSchema):
    name: RoleName
    description: RoleDescription | None = None


class UserSchema(PydanticSchema):
    id: UserID
    username: Username
    is_active: bool
    role: RoleName

class UserAuthSchema(PydanticSchema):
    id: UserID
    username: Username
    role: RoleName
    scopes: RoleScopes


class CreateUserSchema(PydanticSchema):
    username: Username
    password: Password
    role: RoleName

class UpdateUserSchema(PydanticSchema):
    username: Username | None = None
    password: Password | None = None
    is_active: bool | None = None
    role: RoleName | None = None