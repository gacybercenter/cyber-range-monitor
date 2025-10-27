
import sqlalchemy as sa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pwdlib.hashers.argon2 import Argon2Hasher
from pydantic import SecretStr
from pydantic_settings import (
    DotEnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from server.configs.sources import Config, get_app_env, get_secret_settings_source


def get_derived_key(
    fernet_key: str, *, salt: str, pbkdf2_iterations: int, pbkdf2_key_length: int
) -> bytes:
    encoded_salt = salt.encode('utf-8')
    key_bytes = fernet_key.encode('utf-8')
    pdkdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=pbkdf2_key_length,
        salt=encoded_salt,
        iterations=pbkdf2_iterations,
    )
    return pdkdf.derive(key_bytes)


class SecretSettings(Config):
    '''
    Security-related settings
    Load order
    1. Initialization Arguments
    2. Environment Variables
    3. .env, .{APP_ENV}.env
    4. Secrets Directory (secrets/, /run/secrets)
    '''

    jwt_private_key: SecretStr
    jwt_public_key: SecretStr
    jwt_algorithm: str = 'RS256'
    jwt_kid: str = 'v1'

    fernet_key: SecretStr
    pbkdf2_salt: SecretStr
    pbkdf2_iterations: int = 100_000
    pbkdf2_key_length: int = 32

    redis_url: SecretStr
    sqlite_url: str = 'sqlite:///./instance/db.sqlite3'

    argon2_time_cost: int = 2
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4
    argon2_hash_length: int = 32
    argon2_salt_length: int = 16

    def get_redis_url(self, db: int = 0) -> str:
        return f'{self.redis_url.get_secret_value()}/{db}'

    def get_sqlite_url(self, *, sync: bool = False) -> sa.URL:
        url = sa.make_url(self.sqlite_url)
        drivername = 'sqlite' if sync else 'sqlite+aiosqlite'
        return url.set(drivername=drivername)

    @property
    def agron2_hasher(self) -> Argon2Hasher:
        return Argon2Hasher(
            time_cost=self.argon2_time_cost,
            memory_cost=self.argon2_memory_cost,
            parallelism=self.argon2_parallelism,
            hash_len=self.argon2_hash_length,
            salt_len=self.argon2_salt_length,
        )

    model_config = SettingsConfigDict(
        secrets_dir=('secrets', '/run/secrets'),
        extra='ignore',
        validate_assignment=True,
        case_sensitive=False,
        env_nested_delimiter='__',
    )

    @property
    def derived_key(self) -> bytes:
        return get_derived_key(
            self.fernet_key.get_secret_value(),
            salt=self.pbkdf2_salt.get_secret_value(),
            pbkdf2_iterations=self.pbkdf2_iterations,
            pbkdf2_key_length=self.pbkdf2_key_length,
        )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[Config],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        app_env = get_app_env()
        secret_source = get_secret_settings_source(settings_cls, app_env=app_env)
        return (
            init_settings,
            env_settings,
            DotEnvSettingsSource(
                settings_cls,
                env_file=('.env', f'.{app_env}.env')
            ),
            secret_source,
        )
