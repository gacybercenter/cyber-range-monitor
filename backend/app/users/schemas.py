from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import Role
from app.shared.schemas import StrictModel, dt_serializer, AuthForm




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
    role: Annotated[Role, Field(..., title='Role', description='The role of the user')]


class UpdateUserForm(StrictModel):
    username: Annotated[
        Optional[str],
        Field(None)
    ]
    password: Annotated[
        Optional[str],
        Field(None)
    ]
    role: Annotated[
        Optional[Role],
        Field(None)
    ]
