import uuid
from datetime import datetime
from typing import Annotated, Self

from fastapi import Query
from pydantic import Field

from server.app.auth.schema import TokenClaim
from server.app.schema import (
    PageModel,
    PydanticModel,
    RequestBody,
    ResponseModel,
)
from server.enums import UserRoles

SessionID = Annotated[
    str, Field(..., description='The unique identifier of the session.')
]


JTI = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier for the JWT.',
    ),
]
UserID = Annotated[
    uuid.UUID,
    Field(
        ...,
        description='The unique identifier of the user.',
    ),
]

Username = Annotated[
    str,
    Field(
        ...,
        description='The username of the user.',
        min_length=3,
        max_length=128,
        pattern=r'^[a-zA-Z0-9_.-]+$',
    ),
]
Password = Annotated[
    str,
    Field(
        ...,
        description='The password of the user.',
        min_length=3,
        max_length=128,
    ),
]
Role = Annotated[
    UserRoles,
    Field(
        ...,
        description='The role of the user.',
    ),
]


class LoginUserBody(RequestBody):
    username: Username
    password: Password


class LoginUserResponse(ResponseModel):
    claim: TokenClaim
    user_id: UserID
    username: Username
    role: Role


class InternalUser(PydanticModel):
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
    credential_version: int


RoleFilter = Annotated[
    UserRoles,
    Query(description='Filter users by their role.'),
]

LoggedInAfter = Annotated[
    datetime,
    Query(description='Filter users who have logged in after the specified datetime.'),
]

CreatedBy = Annotated[
    Username,
    Query(
        description='Filter users created by the specified username.',
        min_length=3,
        max_length=128,
        pattern=r'^[a-zA-Z0-9_.-]+$',
    ),
]


class UserQuery(RequestBody):
    with_role: RoleFilter | None = None
    logged_in_after: LoggedInAfter | None = None
    created_by: CreatedBy | None = None

    @classmethod
    async def depends(
        cls,
        with_role: RoleFilter | None = None,
        logged_in_after: LoggedInAfter | None = None,
        created_by: CreatedBy | None = None,
    ) -> Self:
        return cls(
            with_role=with_role,
            logged_in_after=logged_in_after,
            created_by=created_by,
        )


class UserPage(PageModel[UserSchema]):
    data: list[UserSchema]


class CreateUserBody(RequestBody):
    username: Username
    password: Password
    role: Role


class PatchUserBody(RequestBody):
    username: Username | None = None
    password: Password | None = None
    role: Role | None = None


class PatchUserProfile(RequestBody):
    username: Username | None = None
    password: Password | None = None
