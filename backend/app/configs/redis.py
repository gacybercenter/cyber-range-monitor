from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from .config_init import settings_config

REDIS_ENV_PREFIX = 'REDIS_'


class RedisConfig(BaseSettings):
    '''The Redis configuration settings
    '''
    HOST: str = Field(
        'localhost',
        description='Host of the redis server'
    )
    PORT: int = Field(
        6379,
        description='Port of the redis server'
    )
    PASSWORD: str = Field(
        'password',
        description='Password for the redis server'
    )
    DB: int = Field(
        0,
        description='Database number for redis',
        ge=0,
        lt=16
    )
    model_config = settings_config(REDIS_ENV_PREFIX)
