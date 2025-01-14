# schemas
import uuid
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import timedelta, datetime
from api.config.settings import app_config
from datetime import datetime, timedelta, timezone


def from_now(total_seconds: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=total_seconds)


class UserOAuthData(BaseModel):
    '''The encoded data stored in the JWT tokens'''
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
            app_config.ACCESS_TOKEN_EXP_SEC
        )
    )


class RefreshTokenPayload(JWTPayload):
    type: str = 'refresh'
    exp: datetime = Field(
        default_factory=lambda: from_now(
            app_config.REFRESH_TOKEN_EXP_SEC
        )
    )
