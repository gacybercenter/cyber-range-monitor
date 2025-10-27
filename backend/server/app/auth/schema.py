from datetime import UTC, datetime
from typing import Literal

from pydantic import ConfigDict, computed_field

from server.app.schema import ResponseModel
from server.enums import UserRoles


class TokenClaim(ResponseModel):
    access_token: str
    refresh_token: str
    token_type: Literal['bearer'] = 'bearer'
    max_age: datetime
    expires: int


class AccessToken(ResponseModel):
    sub: str
    username: str
    scope: UserRoles
    jti: str
    sid: str
    cver: int
    exp: int

    @property
    def expiry(self) -> datetime:
        return datetime.fromtimestamp(self.exp, tz=UTC)


class RefreshToken(ResponseModel):
    sub: str
    jti: str
    sid: str
    cver: int
    exp: int
    iat: int

    @property
    def ttl(self) -> int:
        now = datetime.now(UTC).timestamp()
        return max(0, self.exp - int(now))


class SessionData(ResponseModel):
    model_config = ConfigDict(extra='ignore')

    last_used_at: datetime
    created_at: datetime
    user_id: str
    ip_address: str
    user_agent: str
    username: str
    session_id: str

    def to_hashable(self) -> dict:
        return {
            'last_used_at': self.last_used_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'username': self.username,
        }


class SessionList(ResponseModel):
    sessions: list[SessionData]
    current_session_id: str | None = None

    @computed_field
    @property
    def total(self) -> int:
        return len(self.sessions)
