from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import Role
from app.common.models import StrictModel


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
        min_length=3,
        max_length=128
    )
]

class AuthForm(StrictModel):
    username: FormUsername = Field(..., title='Username', description='The username of the user (min length = 3, max length = 50)') 
    password: FormPassword = Field(..., title='Password', description='The password of the user (min length = 3, max length = 128)')
    
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

class UpdateUserBody(StrictModel):
    username: Optional[FormUsername] 
    password: Optional[FormPassword] 
    role: Optional[Role] 
