from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class RedisConfig(BaseSettings):
    HOST: str = Field(
        'localhost',
        description='Host of the redis server'
    )
    PORT: int = Field(
        6379,
        description='Port of the redis server'
    )
    DB: int = Field(
        0,
        description='Database number for redis'
    )
    PASSWORD: str = Field(
        ..., 
        description='Password for the redis server'
    )

    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
    )
    