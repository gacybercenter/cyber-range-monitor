from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from datetime import timedelta


class Settings(BaseSettings):
    '''The base config for the application'''
    SECRET_KEY: str
    TITLE: str = '[API] Range Monitor v2'
    VERSION: str = '0.1'

    DEBUG: bool = True
    TESTING: bool = False

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int = 0

    DATABASE_URL: str
    DATABASE_ECHO: bool = False

    DATABASE_USE_PRAGMAS: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    JWT_REFRESH_EXP_SEC: int = int(timedelta(days=1).total_seconds())
    JWT_ACCESS_EXP_MIN: int = int(timedelta(minutes=30).total_seconds())

    DOCS_URL: str = '/docs'
    OPENAPI_URL: str = '/openapi.json'
    REDOC_URL: str = '/redoc'

    CONSOLE_LOG: bool = True
    WRITE_LOGS: bool = True
    DELETE_LOGS_AFTER: Optional[int] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
