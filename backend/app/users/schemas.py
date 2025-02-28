from datetime import datetime
from typing import Annotated, Optional

from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import Role
from app.shared.schemas import AuthForm, StrictModel, dt_serializer

UserID = Annotated[int, Path(
    ...,
    description='The id of the user to act on.',
    gt=0
)]


class UserResponse(BaseModel):
    '''The response model for the user; only provides the essential information'''
    id: int
    username: str
    role: Role

    model_config = ConfigDict(
        from_attributes=True
    )


class UserDetailsResponse(UserResponse):
    '''The response model for the user; provides all the information'''
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: dt_serializer
        }
    )


class CreateUserForm(AuthForm):
    '''form to create a user
    '''
    role: Annotated[Role, Field(
        ..., title='Role', description='The role of the user'
    )]


class UpdateUserForm(StrictModel):
    '''form to update a user
    '''
    username: Annotated[Optional[str], Field(None)]
    password: Annotated[Optional[str], Field(None)]
    role: Annotated[Optional[Role], Field(None)]
