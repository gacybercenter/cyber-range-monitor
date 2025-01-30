from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Any
from datetime import timedelta
from pydantic import Field, field_validator
from pathlib import Path

from websockets import Data


DEFAULT_SUMMARY = 'An opensource web application for monitoring the various plugins of the Georgia Cyber Range including Guacamole, Openstack and saltstack.'


class BuildConfig(BaseSettings):
    TITLE: str = 'Range Monitor v2'
    VERSION: str = Field(
        '0.1', description="The build version of the application"
    )
    DEBUG: bool = Field(
        True, description="Whether to run the application in debug mode, DISABLE IN PRODUCTION"
    )
    SUMMARY: str = Field(
        DEFAULT_SUMMARY, description="The summary of the application"
    )
    SECRET_KEY: str = Field(
        ..., description="The secret key for the application, use scripts\\key_gen.py to generate one."
    )
    ALLOW_CONSOLE_LOGGING: bool = Field(
        True, description="Whether to allow console logging, DISABLE IN PRODUCTION"
    )
    USE_SECURE_HEADERS: bool = Field(
        False, description="Whether to use secure headers middleware, ENABLE IN PRODUCTION"
    )


class RedisConfig(BaseSettings):
    REDIS_HOST: str = Field(
        "localhost", description="The host for the Redis server"
    )
    REDIS_PORT: int = Field(
        6379, description="The port for the Redis server"
    )
    REDIS_DB: int = Field(
        0, description="The database number for the Redis server"
    )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class DatabaseConfig(BaseSettings):
    DATABASE_URL: str = Field(..., description="The URL for the database")
    DATABASE_ECHO: bool = Field(
        False,
        description="Whether to echo the database queries into the console, useful for debugging and development"
    )
    DATABASE_USE_PRAGMAS: bool = Field(
        False, description="Whether to use PRAGMA statements for the SQLite databases, use in production for better performance"
    )
    DATABASE_WRITE_LOGS: bool = Field(
        True, description="Whether to log application events into the databse, this should almost always be enabled"
    )
    DATABASE_MAX_LOG_AGE: Optional[int] = Field(
        -1, description="The maximum age of the logs in days, if set to -1 the logs will never be deleted"
    )

    @field_validator('DATABASE_URL', mode='after')
    def validate_database_url(cls, v: str) -> str:
        if not v.startswith('sqlite+aiosqlite:///'):
            raise ValueError(
                "DATABASE_URL must start with 'sqlite+aiosqlite:///'")
        return v

    @classmethod
    def log_age_days(cls) -> Optional[timedelta]:
        if cls.DATABASE_MAX_LOG_AGE < 1:  # type: ignore
            return None
        return timedelta(days=cls.DATABASE_MAX_LOG_AGE)  # type: ignore


class SessionConfig(BaseSettings):
    SESSION_COOKIE_NAME: str = Field(
        'session_id', description="The name of the session cookie"
    )
    SESSION_LIFETIME: int = Field(
        86400, description="The lifetime of the session in seconds, default is 1 day (86400 seconds)"
    )
    SESSION_COOKIE_SECURE: bool = Field(
        False, description="Whether the session cookies should be secure (HTTPS only)"
    )
    SESSION_COOKIE_HTTPONLY: bool = Field(
        False, description="Whether the session cookie should be HTTP only"
    )
    SESSION_COOKIE_SAMESITE: str = Field(
        'lax', description="The SameSite attribute for the session cookie"
    )
    SESSION_HMAC_KEY: str = Field(
        ..., description='The HMAC key for the session cookies, use scripts\\key_gen.py and generate a token hex.'
    )

    @classmethod
    def session_cookie_kwargs(cls, session_id: str) -> dict[str, Any]:
        return {
            'key': cls.SESSION_COOKIE_NAME,
            'value': session_id,
            'httponly': cls.SESSION_COOKIE_HTTPONLY,
            'max_age': cls.SESSION_LIFETIME,
            'expires': cls.SESSION_LIFETIME,
            'secure': cls.SESSION_COOKIE_SECURE,
            'samesite': cls.SESSION_COOKIE_SAMESITE,
            'path': '/'
        }


class DocumentationConfig(BaseSettings):
    DOCS_URL: Optional[str] = Field(
        '/docs',
        description="The URL for the Swagger UI documentation, DISABLE IN PRODUCTION"
    )
    OPENAPI_URL: Optional[str] = Field(
        '/openapi.json',
        description="The URL for the OpenAPI schema, DISABLE IN PRODUCTION"
    )
    REDOC_URL: Optional[str] = Field(
        '/redoc',
        description="The URL for the redoc documentation, DISABLE IN PRODUCTION"
    )

    @staticmethod
    def disabled_documentation() -> 'DocumentationConfig':
        return DocumentationConfig(
            DOCS_URL=None,
            OPENAPI_URL=None,
            REDOC_URL=None
        )
    SettingsConfigDict()


config_prefixes = {
    'db': DatabaseConfig,
    'redis': RedisConfig,
    'session': SessionConfig,
    'docs': DocumentationConfig ,
    'build': BuildConfig
} 


class BaseAppConfig(
    BuildConfig,
    RedisConfig,
    DatabaseConfig,
    SessionConfig,
    DocumentationConfig
):
    pass
