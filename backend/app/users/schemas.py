from datetime import datetime
from typing import Annotated

from fastapi import Path
from pydantic import Field

from app.models.enums import Role
from app.schemas.base import APIRequestModel, AuthForm, CustomBaseModel

UserID = Annotated[int, Path(..., description="The id of model to act on.", gt=0)]


class UserResponse(CustomBaseModel):
    """The response model for the user; only provides the essential information"""

    id: Annotated[int, Field(..., title="ID", description="The ID of the user")]
    username: Annotated[
        str, Field(..., title="Username", description="The username of the user")
    ]
    role: Annotated[Role, Field(..., title="Role", description="The role of the user")]


class UserDetailsResponse(UserResponse):
    """The response model for the user; provides all the information"""

    created_at: Annotated[
        datetime, Field(..., description="The date the user was created")
    ]
    updated_at: Annotated[
        datetime, Field(..., description="The date the user was last updated")
    ]


class CreateUserForm(AuthForm):
    """form to create a user"""

    role: Annotated[Role, Field(..., description="The role of the user")]


class UpdateUserForm(APIRequestModel):
    """form to update a user"""

    username: Annotated[str | None, Field(None)]
    password: Annotated[str | None, Field(None)]
    role: Annotated[Role | None, Field(None)]
