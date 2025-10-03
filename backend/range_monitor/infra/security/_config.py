
from datetime import timedelta
from typing import Literal

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from range_monitor.core.config_class import EnvConfig, TomlSection


class JwtSecrets(EnvConfig):
    '''
    JWT configuration settings, loaded from .env
    '''
    model_config = SettingsConfigDict(env_file='.env')
    jwt_secret_key: str
    jwt_algorithm: Literal['HS256'] = 'HS256'
    jwt_kid: str = 'v1'


class CryptoConfig(EnvConfig):
    '''
    Cryptography configuration settings
    loaded from .env
    '''
    model_config = SettingsConfigDict(env_file='.env')

    fernet_key: str
    bcrypt_pepper: str
    bcrypt_rounds: int = 12
    pbkdf2_iterations: int = 100_000
    pbkdf2_key_length: int = 32


class JwtOptions(TomlSection):
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
