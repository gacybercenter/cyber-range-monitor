import secrets
from datetime import UTC, datetime
from typing import Self

import msgspec


class Session(msgspec.Struct):
    '''
    The encoded session struct stored in redis.
    '''
    user_id: str
    created_at: datetime
    ip_address: str | None
    user_agent: str | None
    session_id: str
    last_seen: datetime


    def touch(self) -> None:
        '''
        Updates the last seen timestamp to now.
        '''
        self.last_seen = datetime.now(tz=self.last_seen.tzinfo)

    @classmethod
    def make_id(cls) -> str:
        return secrets.token_urlsafe(32)
