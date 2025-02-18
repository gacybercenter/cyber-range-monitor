import os
from typing import Optional

from pydantic_settings import SettingsConfigDict
from .base import AppConfig


def env_path(env_name: str) -> str:
    return os.path.join('instance', f'.{env_name}.env')


class ProdConfig(AppConfig):
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
        env_file=env_path('prod'),
        env_file_encoding='utf-8',
        extra='ignore'
    )


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
        env_file=env_path('dev'),
        env_file_encoding='utf-8',
        extra='ignore'
    )


def create_config_mixin(app_env) -> AppConfig:
    '''a very cursed work around to create a mixin for the AppConfig
    Arguments:
        env_path {str} -- env_path name 
    Returns:
        AppConfig -- the mixin create from .<env>.env file
    '''
    path = env_path(app_env)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Unknown APP_ENV: Could not find file  .{app_env}.env at: {path}'
        )

    # this feels illegal
    class _mixin(AppConfig):
        model_config = SettingsConfigDict(
            env_file=path,
            env_file_encoding='utf-8',
            extra='ignore'
        )

    return _mixin()  # type: ignore
