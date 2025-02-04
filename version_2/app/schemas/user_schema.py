from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.user import Role



FormUsername = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=50,
        pattern=r'^[a-zA-Z0-9_.-]+$'
    )
]

FormPassword = Annotated[
    str,
    StringConstraints(
        min_length=6,
        max_length=128
    )
]

class AuthForm(BaseModel):
    username: FormUsername = Field(
        ...,
        description='The username for the auth form.'
    )
    password: FormPassword = Field(
        ...,
        description='The password for the auth form.'
    )

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

    model_config = ConfigDict(from_attributes=True)


class CreateUserBody(AuthForm):
    role: Role = Field(
        default=Role.USER,
        min_length=3,
        max_length=20
    )

class UpdateUserBody(BaseModel):
    username: Optional[FormUsername] 
    password: Optional[FormPassword] = Field(None, max_length=255)
    role: Optional[str] = Field(None, min_length=3, max_length=20)  # type: ignore
