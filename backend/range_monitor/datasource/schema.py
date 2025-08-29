from typing import Annotated

from pydantic import Field

from range_monitor.datasource.types import DataSourceType
from range_monitor.schema import PaginatedList, RequestBody, ResponseModel

DatasourceID = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier of the data source',
        min_length=1,
        max_length=36,
    )
]


DatasourceUsername = Annotated[
    str,
    Field(
        description='The username used to authenticate with the data source',
        min_length=1,
        max_length=255,
    )
]
DatasourcePassword = Annotated[
    str,
    Field(
        description='The password used to authenticate with the data source',
        min_length=1,
        max_length=255,
    )
]

SourceType = Annotated[
    DataSourceType,
    Field(description='The type of data source'),
]

DatasourceEnpoint = Annotated[
    str,
    Field(
        description='The endpoint URL of the data source',
        min_length=1,
        max_length=255,
    )
]


class DataSourceResponse(ResponseModel):
    id: DatasourceID
    username: DatasourceUsername
    type: SourceType
    enabled: bool = Field(..., description='Whether this data source is enabled')

class DataSourceCreateBody(RequestBody):
    username: DatasourceUsername
    password: DatasourcePassword
    type: SourceType

class DatasourceUpdateBody(RequestBody):
    username: DatasourceUsername | None = None
    password: DatasourcePassword | None = None
    enabled: bool | None = None

class DatasourceListResponse(PaginatedList[DataSourceResponse]):
    data: list[DataSourceResponse] = Field(
        ..., description='List of data sources on the current page'
    )



