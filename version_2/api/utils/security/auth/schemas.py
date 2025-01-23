import uuid
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field
from datetime import timedelta, datetime
from api.config import app_config
from datetime import datetime, timedelta, timezone


def from_now(total_seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=total_seconds)


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
    role: str = Field(..., description="The user's role.")
    type: str = 'access'
    exp: datetime = Field(
        default_factory=lambda: from_now(
            app_config.jwt.JWT_ACCESS_EXP_MIN
        )
    )


class RefreshTokenPayload(JWTPayload):
    type: str = 'refresh'
    exp: datetime = Field(
        default_factory=lambda: from_now(
            app_config.jwt.JWT_REFRESH_EXP_SEC
        )
    )
