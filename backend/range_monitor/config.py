from datetime import timedelta
import functools
from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import TomlSection, TomlConfig
from range_monitor.db.config import SqliteConfig
from range_monitor.redis import RedisOptions
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

class LoggerConfig(TomlSection):
    '''config.toml -> [logger]'''
    format: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        'cid=<cyan>{extra[correlation_id]}</cyan> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
        '<level>{message}</level>'
    )
    level: LoguruLevels = 'INFO'
    mute: list[str] = []
    retention_days: int = 7
    rotation_mb: int = 100
    compression: LoguruCompression = 'zip'


class AuthConfig(TomlSection):
    '''config.toml -> [auth]'''
    access_token_expire_minutes: int = Field(
        default=30,
        gt=1,
    )
    refresh_token_expire_hours: int = Field(
        gt=1,
        default=24,
    )
    jwt_issuer: str = 'range-monitor'
    jwt_audience: str = 'range-monitor-users'
    token_leeway_seconds: int = 5

    @property
    def access_delta(self) -> timedelta:
        return timedelta(minutes=self.access_token_expire_minutes)

    @property
    def refresh_delta(self) -> timedelta:
        return timedelta(hours=self.refresh_token_expire_hours)


class CorsConfig(TomlSection):
    '''config.toml -> [cors]'''
    allow_origins: list[str] = ['*']
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']
    allow_credentials: bool = True


class HttpxConfig(TomlSection):
    '''config.toml -> [httpx]'''
    pool_size: int = 15
    max_redirects: int = 5
    limits: dict[str, int | float] = Field(
        default_factory=lambda: {
            'max_keepalive_connections': 5,
            'max_connections': 10,
            'keepalive_expiry': 30.0,
        }
    )
    timeout: dict[str, int | float] = Field(
        default_factory=lambda: {
            'connect': 5.0,
            'read': 10.0,
            'write': 10.0,
            'pool': 5.0,
        }
    )



class AppSettings(TomlConfig):
    '''config.toml'''
    model_config = SettingsConfigDict(
        toml_file='config.toml',
    )

    app: AppConfig
    logger: LoggerConfig
    auth: AuthConfig
    cors: CorsConfig
    httpx: HttpxConfig
    sqlite: SqliteConfig
    redis: RedisOptions


@functools.lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings() # type: ignore

