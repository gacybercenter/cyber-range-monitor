from typing import Optional

from pydantic_settings import SettingsConfigDict
from .base import AppConfig


class ProductionConfig(AppConfig):
    DOCS_OPENAPI_URL: Optional[str] = None
    DOCS_OPENAPI_JSON_URL: Optional[str] = None
    DOCS_REDOC_URL: Optional[str] = None

    COOKIE_SECURE: bool = True
    COOKIE_HTTP_ONLY: bool = True
    COOKIE_SAMESITE: str = 'strict'
    DATABASE_ECHO: bool = False
    DEBUG: bool = False

    VERSION: str = 'v1'

    CONSOLE_LOG: bool = False
    USE_SECURITY_HEADERS: bool = True

    model_config = SettingsConfigDict(
        env_file='.prod.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
