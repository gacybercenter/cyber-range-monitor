import functools
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import TomlConfig

JournalMode = Literal[
    'DELETE',
    'TRUNCATE',
    'PERSIST',
    'MEMORY',
    'WAL',
    'OFF',
]
SynchronousMode = Literal[
    'OFF',
    'NORMAL',
    'FULL',
    'EXTRA',
]
TempStoreMode = Literal[
    'DEFAULT',
    'FILE',
    'MEMORY',
]

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


class TomlSection(BaseModel): ...


class AuthConfig(TomlSection):
    access_toke_expire_minutes: int = Field(
        default=30,
        description='Number of minutes until an access token expires',
        gt=1,
    )
    refresh_token_expire_days: int = Field(
        default=1,
        description='Number of days until a refresh token expires',
        ge=1,
    )
    jwt_issuer: str = Field(
        default='range-monitor',
        description='Issuer to include in JWT tokens',
    )
    jwt_audience: str = Field(
        default='range-monitor-users',
        description='Audience to include in JWT tokens',
    )



class LogConfig(TomlSection):
    """
    Options for logging.

    Parameters
    ----------
    BaseModel : _type_
    """

    level: LoguruLevels = 'INFO'
    directory: str = 'logs'
    rotation_mb: int = 100
    retention_days: int = 7
    compression: LoguruCompression = 'zip'


class DatabaseConfig(TomlSection):
    echo: bool = False
    timeout: int = 30

class AppConfig(TomlSection):
    debug: bool = True
    testing: bool = False
    allow_docs: bool = True
    env_file: str = '.env'
    version: str = '0.1.0'
    root_path: str = ''
    redirect_slashes: bool = True


class CorsConfig(TomlSection):
    allow_origins: list[str] = ['*']
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']
    allow_credentials: bool = True


class RangeMonitorSettings(TomlConfig):
    """
    "Static" configurations for adapters that would've otherwise been constants
    for the specific adapters that are non-sensitive.

    They are loaded from a YAML file titled `adapters.config.yaml` in the
    project root and all arguments are optional, but provide the flexibility
    to easily change configurations as needed
    """

    model_config = SettingsConfigDict(
        yaml_file='config.yml',
    )

    auth: AuthConfig = Field(default_factory=AuthConfig)
    logging: LogConfig = Field(default_factory=LogConfig)
    sql: DatabaseConfig = Field(default_factory=DatabaseConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)

@functools.lru_cache
def get_app_settings() -> RangeMonitorSettings:
    return RangeMonitorSettings()


