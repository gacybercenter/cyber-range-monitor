


from typing import Annotated

from pydantic import Field

from app.core.schema import PydanticSchema

RoleName = Annotated[
    str,
    Field(
        description='The name of the role',
        max_length=64,
    ),
]
RoleDescription = Annotated[
    str | None,
    Field(
        description='A brief description of the role',
        max_length=255,
    ),
]

RoleID = Annotated[
    str,
    Field(description='The unique identifier of the role')
]

RoleLevel = Annotated[
    int,
    Field(description='The level of the role, higher means more privileges', ge=0),
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
    str,
    Field(description='The unique identifier of the user')
]

class RoleSchema(PydanticSchema):
    id: RoleID
    name: RoleName
    description: RoleDescription
    level: RoleLevel

class CreateRoleSchema(PydanticSchema):
    name: RoleName
    level: RoleLevel
    description: RoleDescription = None


class UserSchema(PydanticSchema):
    id: UserID
    username: Username
    is_active: bool
    role: RoleSchema



class CreateUserSchema(PydanticSchema):
    username: Username
    password: Password
    is_active: bool = True
