import uuid
from datetime import datetime
from typing import Literal

import msgspec
from pydantic import Field

from range_monitor.core.enums import UserRoles
from range_monitor.schema.http import RequestBody, ResponseModel


class JwtClaim(msgspec.Struct):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    nbf: int
    jti: str
    token_type: str
    cver: int
    role: UserRoles

    def payload(self) -> dict:
        return {
            "iss": self.iss,
            "sub": self.sub,
            "aud": self.aud,
            "iat": self.iat,
            "exp": self.exp,
            "nbf": self.nbf,
            "jti": self.jti,
            "token_type": self.token_type,
            "cver": self.cver,
            "role": self.role
        }

    @property
    def time_to_live(self) -> int:
        return max(0, self.exp - int(datetime.now().timestamp()))

    @property
    def user_id(self) -> uuid.UUID:
        return uuid.UUID(self.sub)

class RefreshRequest(RequestBody):
    refresh_token: str = Field(
        ...,
        description='The refresh token used to obtain a new access token.'
    )
    access_token: str = Field(
        ...,
        description=(
            'The current access token, if available. This is used to verify '
            'the session and ensure the refresh token is valid.'
        )
    )


class TokenClaim(ResponseModel):
    access_token: str
    refresh_token: str
    token_type: Literal['bearer'] = 'bearer'
    expires_at: int
    issued_at: int

