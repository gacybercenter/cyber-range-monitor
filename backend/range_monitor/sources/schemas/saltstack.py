from typing import Annotated

from pydantic import Field

from range_monitor.schema.http import PageModel
from range_monitor.sources.schemas.base import (
    CreateDatasource,
    DatasourceSchema,
    PatchDatasource,
)

Endpoint = Annotated[
    str,
    Field(
        description='The URL endpoint of the Saltstack API.',
        min_length=1,
        max_length=255,
    ),
]
Hostname = Annotated[
    str,
    Field(
        description='The hostname for the Saltstack API.',
        min_length=1,
        max_length=255,
    ),
]


class SaltstackSchema(DatasourceSchema):
    endpoint: Endpoint
    hostname: Hostname


class SaltstackPage(PageModel[SaltstackSchema]):
    data: list[SaltstackSchema]


class CreateSaltstackBody(CreateDatasource):
    endpoint: Endpoint
    hostname: Hostname


class PatchSaltstackBody(PatchDatasource):
    endpoint: Endpoint | None = None
    hostname: Hostname | None = None
