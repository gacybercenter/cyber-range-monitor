from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from datetime import timedelta
from pydantic import Field


class BaseConfig(BaseSettings):
    '''The base config for the application'''
    SECRET_KEY: str
    TITLE: str = '[API] Range Monitor v2'
    VERSION: str = '0.1'

    DEBUG: bool = True

    REDIS_HOST: str = Field(
        "localhost", description="The host for the Redis server")
    REDIS_PORT: int = Field(6379, description="The port for the Redis server")
    REDIS_DB: int = Field(
        0, description="The database number for the Redis server")

    DATABASE_URL: str = Field(..., description="The URL for the database")
    DATABASE_ECHO: bool = Field(
        False, description="Whether to echo the database queries, useful for debugging and development")

    DATABASE_USE_PRAGMAS: bool = Field(
        False, description="Whether to use PRAGMA statements for the SQLite databases")

    JWT_SECRET_KEY: str = Field(...,
                                description="The secret key for the JWT tokens")
    JWT_ALGORITHM: str = Field(
        'HS256', description="The algorithm for the JWT tokens")

    JWT_REFRESH_EXP_SEC: int = int(timedelta(days=1).total_seconds())
    JWT_ACCESS_EXP_MIN: int = Field(int(timedelta(minutes=30).total_seconds(
    )), description="The expiration time (total seconds) for the access token in minutes")

    DOCS_URL: Optional[str] = Field(
        '/docs', description="The URL for the Swagger UI documentation, DISABLE IN PRODUCTION")
    OPENAPI_URL: Optional[str] = Field(
        '/openapi.json', description="The URL for the OpenAPI schema, DISABLE IN PRODUCTION")
    REDOC_URL: Optional[str] = Field(
        '/redoc', description="The URL for the redoc documentation, DISABLE IN PRODUCTION")

    CONSOLE_LOG: bool = Field(
        True, description="Whether to log to the console")
    WRITE_LOGS: bool = Field(
        True, description="Whether to write logs to a file")
    DELETE_LOGS_AFTER: Optional[int] = Field(
        -1, description="The number of days to keep the logs before deleting them, if set to a negative number they will never be deleted")


class Settings(BaseConfig):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings: Settings = Settings()  # type: ignore
