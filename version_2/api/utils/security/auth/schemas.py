# schemas
from pydantic import BaseModel, Field
from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserOAuthData(BaseModel):
    '''The encoded data stored in the JWT tokens'''
    sub: str  # the username of the user
    role: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    


