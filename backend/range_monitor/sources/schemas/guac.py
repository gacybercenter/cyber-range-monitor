

from typing import Annotated

from pydantic import Field

from range_monitor.schema.http import PageModel
from range_monitor.sources.schemas.base import (
    CreateDatasource,
    DatasourceSchema,
    PatchDatasource,
)

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
    data_source_type: GuacamoleSource


class PatchGuacamoleConfig(PatchDatasource):
    hostname: GuacamoleHostname | None = None
    data_source_type: GuacamoleSource | None = None


class PatchGuacamoleBody(PatchDatasource):
    config: PatchGuacamoleConfig | None = None


class GuacamoleSchema(DatasourceSchema):
    hostname: GuacamoleHostname
    data_source_type: GuacamoleSource


class GuacamolePage(PageModel[GuacamoleSchema]):
    data: list[GuacamoleSchema]
