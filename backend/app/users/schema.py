from datetime import datetime
from typing import Annotated, Self

from pydantic import Field

from app.core.schemas import (
    APIRequestModel,
    AuthForm,
    CustomBaseModel
)
from app.auth.schemas import (
    KeyInfo, APIKeyHealth
)


from .model import Role


class UserResponse(CustomBaseModel):
    """The response model for the user; only provides the essential information """

    id: Annotated[int, Field(..., title="ID",
                             description="The ID of the user")]
    username: Annotated[
        str, Field(..., title="Username",
                   description="The username of the user")
    ]
    role: Annotated[Role, Field(..., title="Role",
                                description="The role of the user")]


class UserDetailsResponse(UserResponse):
    """The response model for the user; provides all the information"""

    created_at: Annotated[
        datetime, Field(
            ...,
            description="The date the user was created"
        )
    ]
    updated_at: Annotated[
        datetime, Field(..., description="The date the user was last updated")
    ]


class CreateUserForm(AuthForm):
    """form to create a user"""
    role: Annotated[Role, Field(
        ...,
        description="The role of the user"
    )]


class UpdateUserForm(APIRequestModel):
    """form to update a user"""

    username: Annotated[str | None, Field(None)] = None
    password: Annotated[str | None, Field(None)] = None
    role: Annotated[Role | None, Field(None)] = None


class KeyContext(APIKeyHealth):
    api_key: Annotated[str, Field(
        ..., description="The API key object"
    )]


class AuthContext(CustomBaseModel):
    user: Annotated[UserResponse, Field(
        ..., description="The user object"
    )]
    auth: Annotated[KeyContext, Field(
        ..., description="The authentication object"
    )]
