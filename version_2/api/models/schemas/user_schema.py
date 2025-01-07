from pydantic import BaseModel, Field, model_validator, ConfigDict
from api.models.user import UserRoles
from enum import Enum
from typing import Optional
from datetime import datetime
from api.models.schemas.shared import SchemaCheck
    

class UserResponse(BaseModel):
    id: int 
    username: str
    permission: str
    password_hash: str 

class ReadUser(UserResponse):
    model_config = ConfigDict(from_attributes=True)

class VerboseReadUser(ReadUser):
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class BaseUser(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    permission: str = Field(
        default=UserRoles.user.value,
        min_length=3,
        max_length=20
    )
    password: str  = Field(..., max_length=255)

    @model_validator(mode='after')
    def check_base_user(cls, v) -> dict:
        if v.permission: 
            SchemaCheck.check_permission(v.permission)
        if v.username: 
            SchemaCheck.no_space(v.username, 'Username')
        if v.password:
            SchemaCheck.no_space(v.password, 'Password')
        return v

class CreateUser(BaseUser):
    '''fields required to create a user'''
    pass 

class UpdateUser(BaseUser):
    '''optional fields for updating a user'''
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    permission: Optional[str] = Field(None, min_length=3, max_length=20)    
    password: Optional[str] = Field(None, max_length=255)   

    

    
    









