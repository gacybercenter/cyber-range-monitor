from datetime import timedelta
import os
from typing import Annotated, Literal

from fastapi import FastAPI
from pydantic import Field, PositiveInt


from .base import SettingsMixin, YamlBaseSettings

AppEnvironment = Literal["container", "local"]
AppMode = Literal["dev", "prod"]
SamesiteTypes = Literal["lax", "strict", "none"]
JournalModeTypes = Literal["DELETE", "TRUNCATE",
                           "PERSIST", "MEMORY", "WAL", "OFF"]


class DocumentationConfig(SettingsMixin):
    """the documentation section"""

    allowed: Annotated[
        bool,
        Field(True, description="Enable the API documentation, DISABLE IN PRODUCTION"),
    ]
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


class CORSConfig(SettingsMixin):
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


class AppConfig(SettingsMixin):
    """the "app" section of the YAML file"""

    environment: Annotated[
        AppEnvironment,
        Field("local", description="The environment the app is running in"),
    ]
    mode: Annotated[AppMode, Field(
        "dev",
        description="The mode the app is running in (i.e whether to do fastapi run or fastapi dev)",
    )]
    config_label: Annotated[str, Field(
        "prod",
        description="The label for the config mapped to the file name (e.g 'dev' -> 'config-dev.yml')",
    )]

    env_file: Annotated[str, Field(
        ".env",
        description="The path to the .env file to load the secrets from."
    )]
    testing: Annotated[bool, Field(False, description="Enable testing mode")]
    debug: Annotated[bool, Field(
        False,
        description="Enables debug mode for fastapi giving tracebacks in 500 errors, DISABLE IN PRODUCTION",
    )]
    min_log_level: Annotated[str, Field(
        "INFO",
        description="Minimum event log level to write to the database"
    )]
    rate_limit: Annotated[str, Field(
        "5/minute",
        description="Number of requests allowed per minute"
    )]
    console_enabled: Annotated[bool, Field(
        True,
        description="Enable the console for the application"
    )]
    
    

class DatabaseConfig(SettingsMixin):
    """the "database" section of the YAML file"""

    url: Annotated[
        str,
        Field(
            "sqlite+aiosqlite:///instance/app.db",
            description="The URL for the database connection",
        )
    ]
    sqlalchemy_echo: Annotated[
        bool,
        Field(True, description="Enable SQLAlchemy queries to be printed to stdout"),
    ]
    timeout: Annotated[
        PositiveInt, Field(
            30, description="Timeout for SQLite connection in seconds")
    ]
    busy_timeout: Annotated[
        PositiveInt, Field(5000, description="Timeout for SQLite busy handler")
    ]
    journal_mode: Annotated[
        JournalModeTypes, Field("WAL", description="Journal mode for SQLite")
    ]

    def resolve_url_dir(self) -> str:
        """Returns the directory path for the SQLite database URL
        Returns:
            str: directory path for the SQLite database URL
        """
        db_path = self.url.split("///")[1]
        return os.path.dirname(db_path)

    def pragmas(self) -> dict:
        """Returns the dictionary of pragmas for the SQLite database
        Returns:
            dict: dictionary of pragmas
        """
        return {
            "journal_mode": self.journal_mode,
            "foreign_keys": "ON",
            "busy_timeout": self.busy_timeout,
        }

    def connect_args(self) -> dict:
        """Returns the dictionary of connect arguments for the SQLite database
        Returns:
            dict: dictionary of connect arguments
        """
        return {
            "check_same_thread": False,
            "timeout": self.timeout,
        }

    def __repr__(self) -> str:
        return f"DatabaseSettings(url={self.url}, sqlalchemy_echo={self.sqlalchemy_echo}, timeout={self.timeout}, busy_timeout={self.busy_timeout}, journal_mode={self.journal_mode})"


class RedisConfig(SettingsMixin):
    """the "redis" section of the YAML file, do not include the password here"""

    host: Annotated[str, Field(
        "localhost", description="Host of the redis server")]
    port: Annotated[
        PositiveInt, Field(
            6379, description="Port of the redis server", lt=65535)
    ]
    db: Annotated[
        int, Field(0, description="Database number for redis (0-15)", le=15, ge=0)
    ]


class APIKeyConfig(SettingsMixin):
    """the "api_key" section of the YAML file"""
    cookie_secure: Annotated[
        bool, Field(False, description="Secure flag for the cookie")
    ]
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
    key_lifetime_days: Annotated[
        PositiveInt,
        Field(
            1,
            description=(
                "Max age of a session in days before "
                "the user must re-authenticate and the session is "
                "deleted in the redis store"
            ),
        ),
    ]

    def cookie_key_lifetime(self) -> int:
        """converts the cookie expiration hours to seconds"""
        return self.cookie_expr_hours * 60 * 60

    def cookie_options(self) -> dict:
        """given a cookie value, the api issues the cookie
        with the set configurations in the settings (reduces typing)

        Arguments:
            cookie_value {str} -- the value of the cookie

        Returns:
            dict -- the kwargs for issuing the cookie
        """
        return {
            "samesite": self.cookie_samesite,
            "secure": self.cookie_secure,
            "httponly": self.cookie_http_only,
            "max_age": self.key_max_lifetime(),
            "expires": self.cookie_key_lifetime(),
        }

    def key_max_lifetime(self) -> int:
        """converts the session lifetime days to seconds
        Returns:
            int -- the session lifetime in seconds
        """
        return int(timedelta(days=self.key_lifetime_days).total_seconds())


class AppSettings(YamlBaseSettings):
    """Represents the "config.yml" file"""
    database: DatabaseConfig
    redis: RedisConfig
    api_key: APIKeyConfig
    app: AppConfig
    documentation: DocumentationConfig
    cors_policy: CORSConfig