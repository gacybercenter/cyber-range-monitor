from typing import Annotated
from pydantic import Field

from app.common.yml_config import YAMLSettings, get_app_config_file

SECTION_NAME = "redis"


class RedisSettings(YAMLSettings):
    host: Annotated[str, Field(
        default="localhost",
        description="The host of the Redis server."
    )]
    port: Annotated[int, Field(
        default=6379,
        description="The port of the Redis server."
    )]
    db: Annotated[int, Field(
        default=0,
        ge=0,
        le=15,
        description="The database number to connect to.",
    )]
    use_password: Annotated[bool, Field(
        default=False,
        description="Whether to use a password for the Redis server."
    )]


redis_settings = RedisSettings.create(
    section_name=SECTION_NAME,
    file_cache=get_app_config_file()
)
