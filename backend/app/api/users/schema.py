from datetime import datetime
from typing import Annotated

from pydantic import Field

from app.common.types import FixedStr
from app.common.schemas.http import RequestSchema, ResponseSchema, ResponseList

from app.api.auth.schema import SessionHealth
from .schema import SessionHealth


from app.core.security.rbac import Role


class UserResponse(ResponseSchema):
    """The response model for the user; only provides the essential information"""

    id: Annotated[int, Field(..., description="The ID of the user")]
    username: Annotated[str, Field(..., description="The username of the user")]
    role: Annotated[Role, Field(..., description="The role of the user")]


class UserListResponse(ResponseList[UserResponse]):
    """The response model for the user list; provides all the information"""

    data: Annotated[list[UserResponse], Field(..., description="The list of users")]


class UserDetailsResponse(UserResponse):
    """The response model for the user; provides all the information"""

    created_at: Annotated[
        datetime, Field(..., description="The date the user was created")
    ]
    updated_at: Annotated[
        datetime, Field(..., description="The date the user was last updated")
    ]


class UserDetailsListResponse(ResponseList[UserDetailsResponse]):
    """The response model for the user; provides all the information"""

    data: Annotated[
        list[UserDetailsResponse], Field(..., description="The list of users")
    ]


class UserCreateBody(RequestSchema):
    """form to create a user"""

    username: Annotated[FixedStr, Field(..., description="The username of the user")]
    password: Annotated[FixedStr, Field(..., description="The password of the user")]
    role: Annotated[Role, Field(..., description="The role of the user")]


class UserUpdateBody(RequestSchema):
    """form to update a user"""

    username: Annotated[str | None, Field(None)] = None
    password: Annotated[str | None, Field(None)] = None
    role: Annotated[Role | None, Field(None)] = None


class SessionContext(ResponseSchema):
    user: Annotated[UserResponse, Field(..., description="The user object")]
    session_id: Annotated[str, Field(..., description="The API key object")]
    health: Annotated[
        SessionHealth, Field(..., description="The authentication object")
    ]
