'''
Responsible for setting up the adapters and security services
in the ASGI lifespan so that the resources are created once
and shared across the application. Also ensures proper
shutdown of the resources when the application stops.

'''
from dataclasses import dataclass
from pathlib import Path
from typing import Self
from urllib.parse import quote_plus

from sqlalchemy import URL

from monitor_api.core import constant, settings

from .adapters import RedisAdapter, SqlAdapter
from .security import EncryptionService, PasswordService, SignatureService


class UrlMaker:
    @staticmethod
    def redis_url(
        *,
        host: str,
        port: int,
        db: int,
        username: str | None = None,
        password: str | None = None,
        ssl: bool = False,
    ) -> str:
        '''
        helper function to create a redis url from components.

        Parameters
        ----------
        host : str
        port : int
        db : int
        username : str | None, optional
        password : str | None, optional
        ssl : bool, optional

        Returns
        -------
        str
        '''
        scheme = 'rediss' if ssl else 'redis'

        auth_part = ''
        if username and password:
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            auth_part = f'{encoded_username}:{encoded_password}@'

        elif password:
            encoded_password = quote_plus(password)
            auth_part = f':{encoded_password}@'

        url = f'{scheme}://{auth_part}{host}:{port}/{db}'

        return url

    @staticmethod
    def sqlite_url(
        *,
        db_dir_path: Path,
        db_filename: str,
        driver_name: str = 'sqlite+aiosqlite',
    ) -> URL:
        '''
        Creates the SQLite url for the database file

        Returns
        -------
        URL
            _description_
        '''
        db_dir_path.mkdir(parents=True, exist_ok=True)
        env_config = settings.get_env_settings()

        if db_filename == ':memory:':
            database_path = env_config.DB_FILENAME
        else:
            database_path = f'{constant.DATABASE_DIRNAME}/{env_config.DB_FILENAME}'

        return URL.create(
            drivername=driver_name,
            database=database_path,
        )


@dataclass(slots=True)
class APIAdapters:
    """
    The I/O bound adapaters (i.e something you connect to)
    that are created at application startup to attached to the asgi lifespan
    state.
    """

    sql: SqlAdapter
    redis: RedisAdapter

    @classmethod
    def build(cls) -> Self:
        env_settings = settings.get_env_settings()
        sqlite_url = UrlMaker.sqlite_url(
            db_dir_path=constant.DATABASE_DIR_PATH,
            db_filename=env_settings.DB_FILENAME,
            driver_name=env_settings.DB_DRIVER_NAME,
        )

        redis_url = UrlMaker.redis_url(
            host=env_settings.REDIS_HOST,
            port=env_settings.REDIS_PORT,
            db=env_settings.REDIS_DB,
            username=env_settings.REDIS_USERNAME,
            password=env_settings.REDIS_PASSWORD,
            ssl=env_settings.REDIS_SSL,
        )

        return cls(
            sql=SqlAdapter(url=sqlite_url),
            redis=RedisAdapter(url=redis_url),
        )


    async def connect_all(self) -> None:
        '''
        Connects all adapters using their respective yaml
        configurations.
        '''
        adapter_configs = settings.get_adapter_settings()
        await self.sql.connect(adapter_configs.sql)
        await self.redis.connect(adapter_configs.redis)

    async def disconnect_all(self) -> None:
        '''
        Disconnects all adapters.
        '''
        await self.sql.disconnect()
        await self.redis.disconnect()

@dataclass(slots=True)
class APISecurity:
    '''
    Represents the bundled security services for the API
    loaded from environment variables at runtime.
    '''
    encryption: EncryptionService
    password: PasswordService
    signature: SignatureService

    @classmethod
    def build(cls) -> Self:
        '''
        Initializes the security services from environment
        variables.

        Returns
        -------
        Self
        '''
        env_settings = settings.get_env_settings()
        encryption_service = EncryptionService.create(
            key=env_settings.ENCRYPTION_KEY,
            salt=env_settings.ENCRYPTION_SALT,
            iterations=env_settings.PBKDF2_ITERATIONS,
            length=env_settings.PBKDF2_LENGTH,
        )
        password_service = PasswordService.create(
            bcrypt_pepper=env_settings.BCRYPT_PEPPER,
        )
        signature_service = SignatureService.create(
            secret_key=env_settings.SECRET_KEY,
            salt=env_settings.SIGNATURE_SALT,
        )

        return cls(
            encryption=encryption_service,
            password=password_service,
            signature=signature_service,
        )


