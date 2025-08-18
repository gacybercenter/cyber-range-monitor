from typing import Annotated, Final

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from app.core.settings import (
    SecretLoader,
    Settings,
    TomlLoader,
    TomlSettings,
)


class RedisSecrets(Settings):
    model_config = SettingsConfigDict(
        env_prefix='REDIS_',
    )

    HOST: str = Field('localhost', description='The host of the Redis server.')
    PORT: int = Field(6379, description='The port of the Redis server.')
    DB: int = Field(0, ge=0, le=15, description='The database number to connect to.')
    USERNAME: str | None = Field(
        None, description='The username for the Redis server, if any.'
    )
    PASSWORD: str | None = Field(
        None, description='The password for the Redis server, if any.'
    )


class RedisClientOptions(TomlSettings):
    socket_connect_timeout: Annotated[
        float,
        Field(
            description='The timeout for connecting to the Redis server in seconds.',
        ),
    ] = 1.0

    socket_timeout: Annotated[
        float,
        Field(
            description='The timeout for reading/writing to the Redis server (seconds).'
        ),
    ] = 5.0

    max_connections: Annotated[
        int, Field(description='The maximum number of connections to the Redis server.')
    ] = 10

    health_check_interval: Annotated[
        int,
        Field(description='The interval in seconds to check the health of Redis'),
    ] = 30


redis_secrets: Final[RedisSecrets] = SecretLoader.load(RedisSecrets)

redis_options: Final[RedisClientOptions] = TomlLoader.load(
    RedisClientOptions,
    section_name='adapters.redis',
)
