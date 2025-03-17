from datetime import timedelta
import time
from typing import Annotated, Literal
from urllib.parse import quote_plus

from pydantic import Field, PositiveInt

from .base import SettingsMixin


SamesiteTypes = Literal["lax", "strict", "none"]


def timedelta_to_secs(delta: timedelta) -> int:
    return int(delta.total_seconds())


KEY_MAX_AGE_DESC = (
    "Max age of an APIKey in days before "
    "the user must re-authenticate and the key is "
    "deleted in the redis store and in the database"
)


class AuthConfig(SettingsMixin):
    '''the "auth" section of the YAML file'''

    cookie_secure: Annotated[bool, Field(
        False,
        description="Secure flag for the cookie"
    )]
    cookie_http_only: Annotated[bool, Field(
        False,
        description="HttpOnly flag for the cookie"
    )]
    cookie_samesite: Annotated[SamesiteTypes, Field(
        "lax",
        description="SameSite flag for the cookie"
    )]
    cookie_exp_hours: Annotated[float, Field(
        1,
        description="Lifetime of the api key cookie in hours before it is deleted on the client",
    )]
    key_max_age_days: Annotated[float, Field(1, description=KEY_MAX_AGE_DESC)]

    def cookie_exp(self) -> int:
        """converts the cookie expiration hours to seconds"""
        return timedelta_to_secs(timedelta(hours=self.cookie_exp_hours))

    def key_max_age(self) -> int:
        """converts the session lifetime days to seconds
        Returns:
            int -- the session lifetime in seconds
        """
        return timedelta_to_secs(timedelta(days=self.key_max_age_days))

    def cookie_options(self) -> dict:
        """given a cookie value, the api issues the cookie
        with the set configurations in the settings (reduces typing)
        Returns:
            dict -- the kwargs for issuing the cookie
        """
        return {
            "samesite": self.cookie_samesite,
            "secure": self.cookie_secure,
            "httponly": self.cookie_http_only,
            "max_age": self.key_max_age(),
            "expires": time.time() + self.cookie_exp(),
        }


class CORSPolicyConfig(SettingsMixin):
    allow_origins: Annotated[list[str], Field(
        ["*"],
        description="List of allowed origins for the CORS policy"
    )]
    allow_credentials: Annotated[bool, Field(
        True,
        description="Allow credentials for the CORS policy, which is necessary for cookies"
    )]
    allow_methods: Annotated[list[str], Field(
        ["*"],
        description="The allowed methods for the CORS policy"
    )]
    allow_headers: Annotated[list[str], Field(
        ["*"],
        description="The allowed headers for the CORS policy"
    )]


class RedisConfig(SettingsMixin):
    host: Annotated[str, Field(
        "localhost",
        description="The hostname for redis"
    )] = "localhost"

    port: Annotated[PositiveInt, Field(
        6379,
        description="The port assigned to redis"
    )]
    db: Annotated[int, Field(
        0,
        description="The database number to connect to on the Redis server",
        ge=0,
        le=15
    )]

    def get_url(self, password: str | None = None) -> str:
        """returns the redis url for connecting to the server"""
        if password:
            password = quote_plus(password)
            return f"redis://:{password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class DocumentationConfig(SettingsMixin):
    """the documentation section of the yml config file"""

    allowed: Annotated[bool, Field(
        True,
        description="Enable the API documentation, DISABLE IN PRODUCTION"
    )]
    swagger_url: Annotated[str, Field(
        "/docs",
        description="The URL for the Swagger UI"
    )]
    redoc_url: Annotated[str, Field(
        "/redoc",
        description="The URL for the ReDoc UI"
    )]
    openapi_json_url: Annotated[str, Field(
        "/openapi.json",
        description="The URL for the OpenAPI JSON"
    )]
