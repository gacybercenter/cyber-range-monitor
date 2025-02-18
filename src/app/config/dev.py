from pydantic_settings import SettingsConfigDict
from .base import AppConfig


class DevConfig(AppConfig):
    DEBUG: bool = True
    WRITE_LOGS: bool = True
    CONSOLE_LOG: bool = True
    USE_SECURITY_HEADERS: bool = False
    DATABASE_ECHO: bool = True

    DOCS_OPENAPI_URL: str = '/docs'
    DOCS_OPENAPI_JSON_URL: str = '/openapi.json'
    DOCS_REDOC_URL: str = '/redoc'
    
    
    model_config = SettingsConfigDict(
        env_file='.dev.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )
    
