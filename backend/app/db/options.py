from pydantic import BaseModel, Field, PositiveInt 

from typing import Annotated



class DatabaseEngineOptions(BaseModel):
    pool_pre_ping: Annotated[bool, Field(
        True,
        description="Enable pool pre-ping to check if the connection is still alive before use."
    )] = True

    pool_recycle: Annotated[PositiveInt, Field(
        1800,
        description="The max age of a connection before it closes and then reopens in seconds."
    )] = 1800

    pool_timeout: Annotated[PositiveInt, Field(
        30,
        description="The seconds to wait for a connection from the pool before a timeout occurs."
    )] = 30

    pool_size: Annotated[PositiveInt, Field(
        10,
        description="The max number of connections to keep in the pool at a time."
    )] = 10

    max_overflow: Annotated[PositiveInt, Field(
        10,
        description="Max number of connections to create beyond the pool size."
    )] = 10
