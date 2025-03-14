from typing import Annotated

from pydantic import BaseModel, Field, PositiveFloat, PositiveInt


class RedisOptions(BaseModel):
    '''options for the redis client'''
    socket_connect_timeout: Annotated[PositiveFloat, Field(gt=0)] = 1
    socket_timeout: Annotated[PositiveFloat, Field(gt=0)] = 5
    max_connections: Annotated[PositiveInt, Field(gt=0)] = 10
    