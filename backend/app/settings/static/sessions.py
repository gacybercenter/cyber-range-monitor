from typing import Annotated, Literal

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings

SamesiteTypes = Literal["lax", "strict", "none"]


class SessionSettings(BaseSettings):
    """the "sessions" section of the YAML file"""

    cookie_name: Annotated[
        str,
        Field("session_id", description="Name of the session cookie stored on the client"),
    ]
    cookie_secure: Annotated[bool, Field(False, description="Secure flag for the cookie")]
    cookie_http_only: Annotated[
        bool, Field(False, description="HttpOnly flag for the cookie")
    ]
    cookie_samesite: Annotated[
        SamesiteTypes, Field("lax", description="SameSite flag for the cookie")
    ]
    cookie_expr_hours: Annotated[
        PositiveInt,
        Field(
            1,
            description="Lifetime of the session cookie in hours before it is deleted on the client",
        ),
    ]
    session_lifetime_days: Annotated[
        PositiveInt,
        Field(
            1,
            description=(
                "Max age of a session in days before "
                "the user must re-authenticate and the session is deleted in the redis store"
            ),
        ),
    ]

    def cookie_expr_seconds(self) -> int:
        """converts the cookie expiration hours to seconds"""
        return self.cookie_expr_hours * 60 * 60

    def cookie_kwargs(self, cookie_value: str) -> dict:
        """given a cookie value, the api issues the cookie
        with the set configurations in the settings (reduces typing)

        Arguments:
            cookie_value {str} -- the value of the cookie

        Returns:
            dict -- the kwargs for issuing the cookie
        """
        return {
            "key": self.cookie_name,
            "value": cookie_value,
            "samesite": self.cookie_samesite,
            "secure": self.cookie_secure,
            "httponly": self.cookie_http_only,
            "max_age": self.cookie_expr_seconds(),
        }

    def session_max_lifetime(self) -> int:
        """converts the session lifetime days to seconds
        Returns:
            int -- the session lifetime in seconds
        """
        return self.session_lifetime_days * 24 * 60 * 60
