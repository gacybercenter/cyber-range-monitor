from typing import Annotated

from pydantic import Field

from server.app.data_sources.schemas.base import (
    CreateDatasource,
    DatasourceSchema,
    PatchDatasource,
)
from server.app.schema import PageModel

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
