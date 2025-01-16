from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from datetime import datetime
from .validate import SchemaCheck
from api.models.user import UserRoles


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=3, max_length=100)

    @model_validator(mode='after')
    def check_creds(cls, v):
        SchemaCheck.no_space(v.username, 'Username')
        SchemaCheck.no_space(v.password, 'Password')
        return v
    
class UserResponse(BaseModel):
    '''The response model for the user; only provides the essential information'''
    id: int
    username: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(UserResponse):
    '''The response model for the user; provides all the information'''
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BaseUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    role: str = Field(
        default=UserRoles.user.value,
        min_length=3,
        max_length=20
    )
    password: str = Field(..., max_length=255)

    @model_validator(mode='after')
    def check_base_user(cls, v):
        if v.role:
            SchemaCheck.check_permission(v.role)

        if v.username:
            SchemaCheck.no_space(v.username, 'Username')

        if v.password:
            SchemaCheck.no_space(v.password, 'Password')

        return v


class CreateUser(BaseUser):
    pass


class UpdateUser(BaseUser):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    role: Optional[str] = Field(None, min_length=3, max_length=20)
    password: Optional[str] = Field(None, max_length=255)
