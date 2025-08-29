import functools
from datetime import timedelta
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import YamlConfig

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


class AdapterSchema(BaseModel): ...


class AuthConfig(AdapterSchema):
    redis_prefix: str = 'sessions:'
    max_age_hours: int = 24
    idle_timeout_mins: int = 60

    @property
    def idle_timeout(self) -> timedelta:
        """
        Returns the idle timeout in seconds.
        """
        return timedelta(minutes=self.idle_timeout_mins)

    @property
    def max_age(self) -> timedelta:
        """
        Returns the maximum age of a session in seconds.
        """
        return timedelta(hours=self.max_age_hours)


class LogConfig(AdapterSchema):
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


class DatabaseConfig(AdapterSchema):
    echo: bool = False
    timeout: int = 30

class AppConfig(AdapterSchema):
    debug: bool = True
    testing: bool = False
    allow_docs: bool = True
    env_file: str = '.env'
    version: str = '0.1.0'
    root_path: str = ''
    redirect_slashes: bool = True


class CorsConfig(AdapterSchema):
    allow_origins: list[str] = ['*']
    allow_methods: list[str] = ['*']
    allow_headers: list[str] = ['*']
    allow_credentials: bool = True


class RangeMonitorSettings(YamlConfig):
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


