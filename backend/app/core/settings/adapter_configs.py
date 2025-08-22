


from datetime import timedelta
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from .interface import YamlConfigLoader

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


class AsyncEngineConfig(BaseModel):

    pool_size: Annotated[int, Field(
        description='The size of the connection pool.'
    )] = 10

    pool_timeout: Annotated[int, Field(
        description='The timeout for acquiring a connection from the pool in seconds.'
    )] = 30

    pool_recycle: Annotated[int, Field(
        description='The number of seconds after which a connection is recycled.'
    )] = 1800

    max_overflow: Annotated[int, Field(
        description='The maximum number of created past pool size.'
    )] = 10

    pool_pre_ping: Annotated[bool, Field(
        description='Whether to enable pre-ping for connections in the pool.'
    )] = True

    pool_use_lifo: Annotated[bool, Field(
        description='Whether to use LIFO (Last In, First Out) for connection pool.'
    )] = False

    future: bool = True

class SqlitePragmas(BaseModel):
    """
    SQLite pragmas for database connection.
    """
    journal_mode: JournalMode = 'WAL'

    synchronous: SynchronousMode = 'NORMAL'

    # The cache size for SQLite in pages. Negative values represent KB.
    cache_size: int = -64_000
    #  This should be set to 1 for foreign keys to be enabled.
    foreign_keys: bool = True

    temp_store: TempStoreMode = 'MEMORY'

    def _args(self) -> dict[str, str | int | bool]:
        """
        Returns the SQLite pragmas as a dictionary.
        """
        return {
            'journal_mode': self.journal_mode,
            'synchronous': self.synchronous,
            'cache_size': self.cache_size,
            'foreign_keys': int(self.foreign_keys),
            'temp_store': self.temp_store,
        }

    def commands(self):
        for k, v in self._args().items():
            yield f"PRAGMA {k} = {v};"


class SqlAdapterConfig(BaseModel):
    seed_file: str | None = None

    pragmas: SqlitePragmas = SqlitePragmas()
    async_engine: AsyncEngineConfig = AsyncEngineConfig()

class RedisOptions(BaseModel):

    # timeout for socket operations in seconds
    socket_timeout: float = 5.0
    # timeout for establishing socket connections in seconds
    socket_connect_timeout: float = 5.0
    # whether to retry operations when a timeout occurs
    retry_on_timeout: bool = True
    # interval between health checks in seconds
    health_check_interval: float = 10.0
    # whether to retry operations when an error occurs
    retry_on_error: bool = True
    # maximum number of connections in the pool
    max_connections: int = 10


class SessionsConfig(BaseModel):

    redis_prefix: str = 'sessions:'
    max_age_hours: int = 24
    idle_timeout_mins: int = 60

    @property
    def idle_timeout(self) -> int:
        """
        Returns the idle timeout in seconds.
        """
        return int(timedelta(minutes=self.idle_timeout_mins).total_seconds())

    @property
    def max_age(self) -> int:
        """
        Returns the maximum age of a session in seconds.
        """
        return int(timedelta(hours=self.max_age_hours).total_seconds())


class OpenapiConfig(BaseModel):

    title: str = 'Range Monitor v2 API'
    description: str = 'API documentation for Range Monitor v2'
    version: str = '0.1.0'
    summary: str | None = None
    root_path: str = ''
    redirect_slashes: bool = True
    openapi_url: str = '/openapi.json'
    docs_url: str = '/docs'
    redoc_url: str = '/redoc'

class LoggingConfig(BaseModel):
    '''
    Options for logging.

    Parameters
    ----------
    BaseModel : _type_
    '''
    level: LoguruLevels = 'INFO'
    directory: str = 'logs'
    rotation_mb: int = 100
    retention_days: int = 7
    compression: LoguruCompression = 'zip'
    format: str = (
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
        '<level>{level: <8}</level> | '
        'cid=<cyan>{extra[correlation_id]}</cyan> | '
        '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
        '<level>{message}</level>'
    )



class AdapterConfigYaml(YamlConfigLoader):
    '''
    "Static" configurations for adapters that would've otherwise been constants
    for the specific adapters that are non-sensitive.

    They are loaded from a YAML file titled `adapters.config.yaml` in the
    project root and all arguments are optional, but provide the flexibility
    to easily change configurations as needed
    '''
    model_config = SettingsConfigDict(
        yaml_file='adapters.config.yaml',
    )

    env_file: str = '.env'

    sql: SqlAdapterConfig = SqlAdapterConfig()
    redis_client: RedisOptions = RedisOptions()
    sessions: SessionsConfig = SessionsConfig()
    logging: LoggingConfig = LoggingConfig()
    openapi: OpenapiConfig = OpenapiConfig()