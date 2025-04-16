from typing import Annotated

from urllib.parse import quote_plus

from pydantic import Field, PositiveInt

from .base import SettingsMixin


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
