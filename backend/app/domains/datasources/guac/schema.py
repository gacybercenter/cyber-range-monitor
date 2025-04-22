from typing import Annotated


from pydantic import Field

from app.core.datasources.schema import (
    DatasourceOptions,
    DatasourceOptionsUpdate,
    DatasourceConnectionArgs,
    DatasourceRequest,
    DatasourceResponse,
    DatasourceUpdate,
    DatasourceListResponse,
)


class GuacamoleOptions(DatasourceOptions):
    '''The options for a Guacamole datasource'''
    datasource: Annotated[str, Field(
        ...,
        description="The name of the Guacamole datasource"
    )]
    


class GuacamoleOptionsUpdate(DatasourceOptionsUpdate):
    """The optional options for updating a Guacamole datasource"""
    datasource: Annotated[
        str | None,
        Field(None, description="The name of the Guacamole datasource"),
    ] = None


class GuacamoleCreate(DatasourceRequest[GuacamoleOptions]):
    pass


class GuacamoleUpdate(DatasourceUpdate[GuacamoleOptionsUpdate]):
    pass


class GuacamoleResponse(DatasourceResponse[GuacamoleOptions]):
    pass


class GuacamoleListResponse(DatasourceListResponse[GuacamoleResponse]):
    pass


class GuacamoleConnectionArgs(DatasourceConnectionArgs):
    '''The keyword arguments to create a guacamole.session instance'''
    host: Annotated[str, Field(
        ..., description="The Guacamole host to connect to"
    )]
    username: Annotated[str, Field(
        ..., description="The Guacamole username to connect with"
    )]
    password: Annotated[str, Field(
        ..., description="The Guacamole password to connect with"
    )]
    data_source: Annotated[str, Field(
        ..., description="The Guacamole datasource to connect to"
    )]
