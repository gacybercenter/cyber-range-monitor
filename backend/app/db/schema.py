
from typing import Annotated
from pydantic import Field, PositiveInt
from pydantic import Field, PositiveInt
from typing import Annotated, List

from app.common.schemas.base import CustomBaseModel


class DatabaseTableMeta(CustomBaseModel):
    '''metadata of a database table for health tracking purposes'''
    row_count: Annotated[PositiveInt, Field(
        0,
        description="The size of the database table in bytes."
    )] = 0
    table_name: Annotated[str, Field(
        ...,
        description="The name of the database table."
    )]
    read_time: Annotated[float, Field(
        ...,
        description="The time it took to read all rows."
    )]


class DatabaseHealthData(CustomBaseModel):
    '''The response model for a database health check.'''
    server_version: Annotated[str, Field(
        ...,
        description="The version of the database server."
    )]
    driver: Annotated[str, Field(
        ...,
        description="Information related to the driver used for the database."
    )]
    table_meta: Annotated[List[DatabaseTableMeta], Field(
        ...,
        description="The metadata for the database tables."
    )]
