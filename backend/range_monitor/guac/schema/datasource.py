


from typing import Annotated

from pydantic import Field

from range_monitor.datasource.schema import (
    DataSourceCreateBody,
    DatasourceListResponse,
    DataSourceResponse,
    DatasourceUpdateBody,
)

GuacamoleDatasouce = Annotated[
    str,
    Field(
        description='The Guacamole data source identifier',
        min_length=1,
        max_length=32,
    ),
]

GuacamoleEndpoint = Annotated[
    str,
    Field(
        description='The endpoint URL of the data source',
        min_length=1,
        max_length=255,
    ),
]


class GuacamoleResponse(DataSourceResponse):
    endpoint: GuacamoleEndpoint
    datasource: GuacamoleDatasouce


class UpdateGuacamoleBody(DatasourceUpdateBody):
    endpoint: GuacamoleEndpoint | None = None
    datasource: GuacamoleDatasouce | None = None


class CreateGuacamoleBody(DataSourceCreateBody):
    endpoint: GuacamoleEndpoint
    datasource: GuacamoleDatasouce

class GuacamoleListResponse(DatasourceListResponse):
    data: list[GuacamoleResponse] = Field(
        ...,
        description='List of data sources on the current page'
    )