

from typing import Annotated

from pydantic import Field

from range_monitor.datasource.schema import (
    CreateDatasource,
    DatasourceSchema,
    PatchDatasource,
)
from range_monitor.schema import PaginatedList

GuacamoleSource = Annotated[
    str,
    Field(
        description='The Guacamole data source identifier',
        min_length=1,
        max_length=32,
    ),
]

GuacamoleHostname = Annotated[
    str,
    Field(
        description='The endpoint URL of the data source',
        min_length=1,
        max_length=255,
    ),
]



class CreateGuacamoleBody(CreateDatasource):
    hostname: GuacamoleHostname
    datasource_type: GuacamoleSource



class PatchGuacamoleConfig(PatchDatasource):
    hostname: GuacamoleHostname | None = None
    datasource_type: GuacamoleSource | None = None

class PatchGuacamoleBody(PatchDatasource):
    config: PatchGuacamoleConfig | None = None


class GuacamoleResponse(DatasourceSchema):
    hostname: GuacamoleHostname
    datasource_type: GuacamoleSource


class GuacamolePage(PaginatedList[GuacamoleResponse]):
    data: list[GuacamoleResponse]