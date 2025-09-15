

from typing import Literal

from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import EnvConfig


class JwtConfig(EnvConfig):
    '''
    JWT configuration settings, loaded from .env
    '''
    model_config = SettingsConfigDict(
        env_prefix='JWT_'
    )

    secret_key: str
    algorithm: Literal['HS256'] = 'HS256'
    kid: str = 'v1'


class CryptoConfig(EnvConfig):
    '''
    Cryptography configuration settings
    loaded from .env
    '''
    fernet_key: str
    password_salt: str
    pbkdf2_iterations: int = 100_000
    pbkdf2_key_length: int = 32


