import functools
from typing import Literal

from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import TomlConfig, TomlSection
from range_monitor.infra.db import SqliteConfig
from range_monitor.infra.log import LoggerConfig
from range_monitor.infra.redis import RedisOptions
from range_monitor.infra.security import JwtOptions
from range_monitor.infra.adapters import HttpxConfig
from range_monitor.middleware.config import CorsConfig

LoguruLevels = Literal[
    'TRACE',
    'DEBUG',
    'INFO',
    'SUCCESS',
    'WARNING',
    'ERROR',
    'CRITICAL',
]

LoguruCompression = Literal['zip', 'tar', 'gz', 'bz2', 'xz', 'none']


class AppOptions(TomlSection):
    '''config.toml -> [app.options]'''
    debug: bool = False
    testing: bool = False
    allow_docs: bool = True

class AppConfig(TomlSection):
    '''config.toml -> [app]'''
    title: str
    description: str
    summary: str
    version: str = '0.1.0'
    openapi_url: str = '/openapi.json'
    docs_url: str = '/docs'
    options: AppOptions


class AppSettings(TomlConfig):
    '''config.toml'''
    model_config = SettingsConfigDict(
        toml_file='config.toml',
    )

    app: AppConfig
    logger: LoggerConfig
    jwt: JwtOptions
    cors: CorsConfig
    sqlite: SqliteConfig
    redis: RedisOptions
    httpx: HttpxConfig

@functools.lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings() # type: ignore

