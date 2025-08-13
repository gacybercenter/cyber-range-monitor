from datetime import datetime
from typing import Literal, TypeAlias

from fastapi import Body, Path, Query
from pydantic import Field
from test.test_typing import Annotated

from app.core.pydantic import FixedStr
from app.infrastructure.security.roles import Role

from .interface import (
    AuditedQueryParams,
    PageMixin,
    PageQueryParams,
    RequestSchema,
    ResponseSchema,
)

UserID = Annotated[str, Field(..., description='The unique identifier of the user')]
Username = Annotated[FixedStr, Field(..., description='The username of the user')]
Password = Annotated[FixedStr, Field(..., description='The password of the user')]
UserRole = Annotated[Role, Field(..., description='The role of the user')]
UserSorts: TypeAlias = Literal[
    'role',
    'username',
]

QueryRole = Annotated[Role | None, Query(None, description='Filter users by role')]
QueryUserSorts = Annotated[
    UserSorts, Query(default='username', description='The field to sort users by')
]


class UserModel(ResponseSchema):
    id: UserID
    username: Username
    role: UserRole


class UserQueryParams(AuditedQueryParams, PageQueryParams):
    """The query parameters for the user; used to filter and paginate users"""

    role: QueryRole
    sort_by: QueryUserSorts = 'username'



class DetailedUser(UserModel):
    """The response model for the user; provides all the information"""

    created_at: datetime = Field(..., description='The date the user was created')
    updated_at: datetime = Field(..., description='The date the user was last updated')

class UserPage(PageMixin[UserModel]):
    """The response model for the user; provides the essential information and pagination"""

    data: list[UserModel] = Field(..., description='The list of users')


class DetailedUserPage(PageMixin[DetailedUser]):
    data: list[DetailedUser] = Field(
        ..., description='The list of users with detailed information'
    )


class UserCreateModel(RequestSchema):
    username: Username
    password: Password
    role: UserRole


class PublicUserUpdateModel(RequestSchema):
    """form to update a user"""

    username: Username | None
    password: Password | None


class PrivateUserUpdateModel(PublicUserUpdateModel):
    role: UserRole | None


UpdateUserRequest = Annotated[
    PublicUserUpdateModel,
    Body(
        ...,
        description='The request body to update a user; only username and password are allowed',
    ),
]

AdminUpdateUserRequest = Annotated[
    PrivateUserUpdateModel,
    Body(
        ...,
        description='The request body to update a user; username, password, and role are allowed',
    ),
]

CreateUserRequest = Annotated[
    UserCreateModel,
    Body(
        ...,
        description='The request body to create a user; username, password, and role are required',
    ),
]

UserIdPath = Annotated[
    UserID,
    Path(
        ...,
        description='The unique identifier of the user to perform the operation on',
        example='123e4567-e89b-12d3-a456-426614174000',
    ),
]
