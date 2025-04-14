from typing import Annotated

from pydantic import Field

from app.datasource.base.schema import (
    ConnectionTestResult,
    DatasourceConnectionModel,
    DatasourceCreateModel,
    DatasourceReadModel,
    DatasourceUpdateModel,
    DatasourceListResponse,
    FixedStr
)


class GuacamoleRead(DatasourceReadModel):
    """A guacamole datasource schema from the DB"""
    datasource: Annotated[
        str, Field(..., description="The name of the Guacamole datasource")
    ]


class GuacamoleCreate(DatasourceCreateModel):
    """The data for creating a new Guacamole datasource"""
    datasource: Annotated[FixedStr, Field(
        ...,
        description="The name of the Guacamole datasource"
    )]


class GuacamoleUpdate(DatasourceUpdateModel):
    """The data for updating a Guacamole datasource"""

    datasource: Annotated[
        FixedStr | None,
        Field(None, description="The name of the Guacamole datasource"),
    ]
    password: Annotated[
        FixedStr | None,
        Field(None, description="The password for the Guacamole datasource"),
    ]


class GuacamoleListResponse(DatasourceListResponse[GuacamoleRead]):
    """The response for listing Guacamole datasources"""
    data: list[GuacamoleRead]


class GuacamoleSessionConfig(DatasourceConnectionModel):
    host: Annotated[str, Field(..., description="The Guacamole host to connect to")]
    username: Annotated[str, Field(..., description="The Guacamole username to connect with")]
    password: Annotated[str, Field(..., description="The Guacamole password to connect with")]
    data_source: Annotated[str, Field(..., description="The Guacamole datasource to connect to")]


class GuacamoleConnectionResults(ConnectionTestResult):

    @classmethod
    def create(cls, success: bool) -> 'GuacamoleConnectionResults':
        msg = 'Sucessfully created a Guacamole session.'
        if not success:
            msg = 'Failed to create a Guacamole session likely due to improper configurations, please try again.'
        return cls(
            message=msg,
            success=success,
            error=None
        )
