
from typing import Annotated
from app.common.yml_settings import YMLBuildSettings, get_yml_file_section
from pydantic import Field

SECTION_NAME = "redis"


class RedisSettings(YMLBuildSettings):
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
        description="The database number to connect to.",
        ge=0,
        le=15
    )]
    use_password: Annotated[bool, Field(
        default=False,
        description="Whether to use a password for the Redis server."
    )]


redis_settings = RedisSettings.load(
    get_yml_file_section(SECTION_NAME)
)
