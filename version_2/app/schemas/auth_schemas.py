import uuid
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from datetime import timedelta, datetime
from app.core import settings
from datetime import datetime, timedelta, timezone
from enum import StrEnum

def from_now(total_seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=total_seconds)


class TokenTypes(StrEnum):
    ACCESS = 'access'
    REFRESH = 'refresh'


class UserOAuthData(BaseModel):
    '''
    The encoded data stored in the JWT tokens, the sub is the user name
    since we've had issues previously with the user id (that are autoincremented)
    not being unique 
    '''
    sub: str
    role: str


class EncodedToken(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class JWTPayload(BaseModel):
    sub: str = Field(..., description="The subject (user identifier).")
    exp: datetime
    iat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    jti: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
    )
    role: str


class AccessTokenPayload(JWTPayload):
    sub: str = Field(..., description="The subject (user identifier).")
    iat: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    jti: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
    )
    role: str
    exp: datetime = Field(
        default_factory=lambda: from_now(settings.JWT_ACCESS_EXP_MIN),
        description="The expiration time of the access token."
    )


class SessionData(BaseModel):
    access_token: str = Field(..., description="The encoded JWT access token")
    session_id: str = Field(..., description="The unique session id ")
    token_type: str = 'bearer'
