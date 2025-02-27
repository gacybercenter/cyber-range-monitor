from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    '''the "redis" section of the YAML file, do not include the password here'''
    host: Annotated[str, Field(
        'localhost',
        description='Host of the redis server'
    )]
    port: Annotated[PositiveInt, Field(
        6379,
        description='Port of the redis server',
        lt=65535
    )]
    db: Annotated[PositiveInt, Field(
        0,
        description='Database number for redis (0-15)',
        le=15
    )]
