from typing import Any
from pydantic_settings import BaseSettings
from pydantic import Field


class CookieConfig(BaseSettings):
    SESSION_COOKIE: str = Field(
        'session_id', description='Name of the session cookie'
    )
    COOKIE_SECURE: bool = Field(
        False, description='Secure flag for the cookie'
    )
    COOKIE_HTTP_ONLY: bool = Field(
        True, description='HttpOnly flag for the cookie'
    )
    COOKIE_SAMESITE: str = Field(
        'lax', description='SameSite flag for the cookie'
    )
    SESSION_EXPIRATION_SEC: int = Field(
        3600, description='Lifetime of the session in seconds'
    )
    SESSION_MAX_AGE: int = Field(
        84600, description='Max age of the session in seconds'
    )

    
    def cookie_kwargs(self, cookie_value: Any) -> dict:
        return {
            'key': self.SESSION_COOKIE,
            'value': cookie_value,
            'samesite': self.COOKIE_SAMESITE,
            'secure': self.COOKIE_SECURE,
            'httponly': self.COOKIE_HTTP_ONLY,
            'max_age': self.SESSION_EXPIRATION_SEC
        }


class RedisConfig(BaseSettings):
    REDIS_DB: int = Field(
        0, description='Database number for redis'
    )
    REDIS_HOST: str = Field(
        'localhost', description='Host of the redis server'
    )
    REDIS_PORT: int = Field(
        6379, description='Port of the redis server'
    )
    REDIS_PASSWORD: str = Field(
        'password', description='Password for the redis server'
    )


class SecurityConfig(BaseSettings):
    SECRET_KEY: str = Field(
        ..., description='Secret key of the application'
    )
    SIGNATURE_SALT: str = Field(
        ..., description='Salt for the servers signature'
    )
    ENCRYPTION_KEY: str = Field(
        ..., description='Key for encrypting the session'
    )
    RATE_LIMIT: str = Field(
        '5/minute', description='Number of requests allowed per minute'
    )
    CSRF_SECRET_KEY: str = Field(
        ...,
        description='Key for CSRF protection'
    )


class DatabaseConfig(BaseSettings):
    DATABASE_URL: str = Field(
        ..., 
        description='URL for the database connection'
    )
    DATABASE_ECHO: bool = Field(
        True, description='Echo SQL queries to stdout'
    )
    


class BuildConfig(BaseSettings):
    TITLE: str = 'FastAPI FullstackSession Based Auth Template'
    VERSION: str = Field('dev', description='Version of the application')
    SECRET_KEY: str = Field(..., description='Secret key for the app')
    

    DEBUG: bool = Field(
        False, description='Debug mode for the application'
    )
    WRITE_LOGS: bool = Field(
        True, description='Write logs to the database'
    )
    CONSOLE_LOG: bool = Field(
        True, 
        description='Write event logs to the console or not'
    )
    USE_SECURITY_HEADERS: bool = Field(
        False, description='Use the Security Header middleware for all requests, disable in dev'
    )

class BaseAppConfig(
    CookieConfig,
    RedisConfig,
    SecurityConfig,
    DatabaseConfig,
    BuildConfig
):
    pass
