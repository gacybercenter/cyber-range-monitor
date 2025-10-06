import uuid
from typing import Annotated

from pydantic import Field

from range_monitor.schema.http import RequestBody, ResponseModel

DatasourceID = Annotated[
    uuid.UUID,
    Field(
        ...,
        description='The unique identifier for the datasource',
    )
]

DatasourcePassword = Annotated[
    str,
    Field(
        description='The password for the datasource',
        min_length=8,
        max_length=128,
    )
]


DatasourceLabel = Annotated[
    str,
    Field(
        description='A human-readable label for the datasource',
        min_length=1,
        max_length=64,
    )
]

DatasourceDesc = Annotated[
    str,
    Field(
        default=None,
        description='An optional description for the datasource',
        max_length=256,
    )
]

DatasourceUsername = Annotated[
    str,
    Field(
        ...,
        description='The unique name of the datasource',
        min_length=1,
        max_length=128,
    )
]


class DatasourceSchema(ResponseModel):
    id: DatasourceID
    username: DatasourceUsername
    label: DatasourceLabel
    connected: bool
    description: DatasourceDesc | None = None


class CreateDatasource(RequestBody):
    username: DatasourceUsername
    password: DatasourcePassword
    label: DatasourceLabel
    description: DatasourceDesc | None = None


class PatchDatasource(RequestBody):
    label: DatasourceLabel | None = None
    password: DatasourcePassword | None = None
    description: DatasourceDesc | None = None
    username: DatasourceUsername | None = None
