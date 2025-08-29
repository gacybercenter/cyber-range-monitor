from typing import Annotated, Literal

from pydantic import Field

from range_monitor.datasource.schema import (
    DataSourceCreateBody,
    DatasourceListResponse,
    DataSourceResponse,
    DatasourceUpdateBody,
)
from range_monitor.datasource.types import DataSourceType

SaltStackHostname = Annotated[
    str,
    Field(
        description='The hostname of the SaltStack master',
        min_length=1,
        max_length=255,
    ),
]


class SaltStackResponse(DataSourceResponse):
    type: Literal[DataSourceType.SALTSTACK] = DataSourceType.SALTSTACK
    hostname: SaltStackHostname

class CreateSaltStackBody(DataSourceCreateBody):
    type: Literal[DataSourceType.SALTSTACK] = DataSourceType.SALTSTACK
    hostname: SaltStackHostname


class UpdateSaltStackBody(DatasourceUpdateBody):
    hostname: SaltStackHostname | None = None

class SaltStackListResponse(DatasourceListResponse):
    data: list[SaltStackResponse] = Field(
        ...,
        description='List of SaltStack data sources on the current page'
    )