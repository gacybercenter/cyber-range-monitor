from datetime import timedelta
from typing import Any
from pydantic_settings import BaseSettings
from pydantic import Field


class SessionConfig(BaseSettings):
    SESSION_COOKIE: str = Field(
        'session_id',
        description='Name of the session cookie'
    )
    COOKIE_SECURE: bool = Field(
        False,
        description='Secure flag for the cookie'
    )
    COOKIE_HTTP_ONLY: bool = Field(
        False,
        description='HttpOnly flag for the cookie'
    )
    COOKIE_SAMESITE: str = Field(
        'lax',
        description='SameSite flag for the cookie'
    )
    COOKIE_EXPIRATION_HOURS: int = Field(
        1,
        description='Lifetime of the session in seconds'
    )
    SESSION_LIFETIME_DAYS: int = Field(
        1,
        description='Max age of the session in seconds'
    )

    def session_lifetime(self) -> int:
        return int(
            timedelta(days=self.SESSION_LIFETIME_DAYS).total_seconds()
        )

    def cookie_expr(self) -> int:
        return int(
            timedelta(hours=self.COOKIE_EXPIRATION_HOURS).total_seconds()
        )

    def cookie_kwargs(self, cookie_value: Any) -> dict:
        return {
            'key': self.SESSION_COOKIE,
            'value': cookie_value,
            'samesite': self.COOKIE_SAMESITE,
            'secure': self.COOKIE_SECURE,
            'httponly': self.COOKIE_HTTP_ONLY,
            'max_age': self.cookie_expr()
        }
