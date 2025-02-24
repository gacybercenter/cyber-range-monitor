from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class SecurityConfig(BaseSettings):
    SECRET_KEY: str = Field(
        ...,
        description='Secret key of the application'
    )
    SIGNATURE_SALT: str = Field(
        ...,
        description='Salt for the servers signature'
    )
    ENCRYPTION_KEY: str = Field(
        ...,
        description='Key for encrypting the session'
    )
    CSRF_SECRET_KEY: str = Field(
        ...,
        description='Key for CSRF protection'
    )
    REDIS_PASSWORD: str = Field(
        ...,
        description='Password for the redis server'
    )
    SESSION_LIFETIME_DAYS: int = Field(
        1,
        description='Number of days the session is valid for'
    )
