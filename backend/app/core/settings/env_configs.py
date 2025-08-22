
import uuid
from typing import Literal

from pydantic_settings import SettingsConfigDict

from .interface import EnvConfigLoader

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


class DatabaseConfig(EnvConfigLoader):
    """
    Env prefix is DATABASE_
    """

    model_config = SettingsConfigDict(env_prefix='DATABASE_')

    DRIVER_NAME: str = 'sqlite+aiosqlite'
    DIRECTORY: str | None = None
    NAME: str | None = None
    ECHO: bool = False
    JOURNAL_MODE: Literal['WAL', 'DELETE'] = 'WAL'
    SYNCHRONOUS: str = 'NORMAL'
    CACHE_SIZE: int = -64000
    FOREIGN_KEYS: bool = True
    TEMP_STORE: Literal['MEMORY', 'DEFAULT'] = 'MEMORY'


    @property
    def url_parts(self) -> str:
        return (
            f'{self.DIRECTORY}/{self.NAME}'
            if self.NAME != ':memory:'
            else self.NAME
        )

    def get_pragmas(self) -> dict[str, str | int]:
        '''
        The sqlite prgamas to be used for the database
        connection.

        Returns
        -------
        dict[str, str | int]
        '''
        return {
            'journal_mode': self.JOURNAL_MODE,
            'synchronous': self.SYNCHRONOUS,
            'cache_size': self.CACHE_SIZE,
            'foreign_keys': int(self.FOREIGN_KEYS),
            'temp_store': self.TEMP_STORE,
        }

class RedisConfig(EnvConfigLoader):
    """
    Env prefix is REDIS_
    """

    model_config = SettingsConfigDict(env_prefix='REDIS_')

    HOST: str = 'localhost'
    PORT: int = 6379
    DB: int = 0
    USERNAME: str | None = None
    PASSWORD: str | None = None
    SSL: bool = False


class AppConfig(EnvConfigLoader):
    """
    Env prefix is APP_
    """

    model_config = SettingsConfigDict(env_prefix='APP_')

    DEBUG: bool = False
    TESTING: bool = False
    ALLOW_DOCS: bool = False


class CryptoConfig(EnvConfigLoader):
    '''
    Cryptography settings for the application.
    '''
    SECRET_KEY: str
    SIGNATURE_SALT: str

    ENCRYPTION_KEY: str
    ENCRYPTION_SALT: str
    PBKDF2_ITERATIONS: int = 100_000
    PBKDF2_LENGTH: int = 32
    BCRYPT_PEPPER: str


class CorsConfig(EnvConfigLoader):
    model_config = SettingsConfigDict(env_prefix='CORS_')

    ALLOW_ORIGINS: list[str] = ['*']
    ALLOW_METHODS: list[str] = ['*']
    ALLOW_HEADERS: list[str] = ['*']
    ALLOW_CREDENTIALS: bool = True


class CorrelationIdConfig(EnvConfigLoader):
    model_config = SettingsConfigDict(env_prefix='CORRELATION_ID_')

    HEADER_NAME: str = 'X-Request-ID'
    UPDATE_REQUEST_HEADER: bool = True

    def make_id(self) -> str:
        """
        Generates a new UUID for the correlation ID.

        Returns
        -------
        uuid.UUID
            A new UUID instance.
        """
        return str(uuid.uuid4())


class MiddlewareConfig(EnvConfigLoader):
    cors: CorsConfig
    correlation_id: CorrelationIdConfig

class APISettings(EnvConfigLoader):
    '''
    Settings loaded from a `.env` file or
    environment variables for the application.
    '''

    app: AppConfig
    db: DatabaseConfig
    redis: RedisConfig
    middleware: MiddlewareConfig
    crypto: CryptoConfig

