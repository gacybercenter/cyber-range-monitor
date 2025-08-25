from datetime import timedelta
from typing import Annotated, Literal

from pydantic import BaseModel, Field
from pydantic_settings import SettingsConfigDict

from .interface import EnvConfig, YamlConfig

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


class SqlalchemyConfig(AdapterSchema):
    seed_file: str | None = None

    pool_size: Annotated[int, Field(description='The size of the connection pool.')] = (
        10
    )

    pool_timeout: Annotated[
        int,
        Field(
            description='The timeout for acquiring a connection from the pool in seconds.'
        ),
    ] = 30

    pool_recycle: Annotated[
        int,
        Field(
            description='The number of seconds after which a connection is recycled.'
        ),
    ] = 1800

    max_overflow: Annotated[
        int, Field(description='The maximum number of created past pool size.')
    ] = 10

    pool_pre_ping: Annotated[
        bool,
        Field(description='Whether to enable pre-ping for connections in the pool.'),
    ] = True

    pool_use_lifo: Annotated[
        bool,
        Field(
            description='Whether to use LIFO (Last In, First Out) for connection pool.'
        ),
    ] = False

    future: bool = True
    echo: bool = False
    timeout: int = 30  # timeout for database connections in seconds

    @property
    def engine_kwargs(self) -> dict:
        return self.model_dump(exclude={'seed_file', 'timeout'})


class RedisClientConfig(AdapterSchema):
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


class AppConfig(AdapterSchema):
    debug: bool = False
    testing: bool = False
    allow_docs: bool = True
    env_file: str = '.env'
    version: str = '0.1.0'
    root_path: str = ''
    redirect_slashes: bool = True


class AdapterSettings(YamlConfig):
    """
    "Static" configurations for adapters that would've otherwise been constants
    for the specific adapters that are non-sensitive.

    They are loaded from a YAML file titled `adapters.config.yaml` in the
    project root and all arguments are optional, but provide the flexibility
    to easily change configurations as needed
    """

    model_config = SettingsConfigDict(
        yaml_file='adapters.yml',
    )

    sql: SqlalchemyConfig = Field(default_factory=SqlalchemyConfig)
    redis: RedisClientConfig = Field(default_factory=RedisClientConfig)
    sessions: AuthConfig = Field(default_factory=AuthConfig)
    logging: LogConfig = Field(default_factory=LogConfig)
    app: AppConfig = Field(default_factory=AppConfig)


class EnvSettings(EnvConfig):
    """
    Settings loaded from a `.env` file or
    environment variables for the application.
    """

    CORS_ALLOW_ORIGINS: list[str] = ['*']
    CORS_ALLOW_METHODS: list[str] = ['*']
    CORS_ALLOW_HEADERS: list[str] = ['*']
    CORS_ALLOW_CREDENTIALS: bool = True

    DB_DRIVER_NAME: str = 'sqlite+aiosqlite'
    DB_FILENAME: str = 'app.db'
    SECRET_KEY: str
    SIGNATURE_SALT: str

    ENCRYPTION_KEY: str
    ENCRYPTION_SALT: str
    PBKDF2_ITERATIONS: int = 100_000
    PBKDF2_LENGTH: int = 32
    BCRYPT_PEPPER: str
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USERNAME: str | None = None
    REDIS_PASSWORD: str | None = None
    REDIS_SSL: bool = False


