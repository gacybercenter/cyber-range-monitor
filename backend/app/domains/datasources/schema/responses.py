
from typing import Annotated, Union

from app.core.schemas import CustomBaseModel, APIListResponse
from pydantic import Field

from ..salt_stack.schema import (
    SaltstackCreate,
    SaltstackUpdate,
    SaltstackResponse
)

from ..guac.schema import (
    GuacamoleCreate,
    GuacamoleUpdate,
    GuacamoleResponse
)
from ..open_stack.schema import (
    OpenstackCreate,
    OpenstackUpdate,
    OpenstackResponse
)

# defines the union type defintions for OpenAPI, response schemas and
# wrapper objects in one place to avoid circular imports

DatasourceResponses = Union[
    OpenstackResponse, GuacamoleResponse, SaltstackResponse
]

DatasourceListResponses = Union[
    APIListResponse[OpenstackResponse],
    APIListResponse[GuacamoleResponse],
    APIListResponse[SaltstackResponse]
]

CreateSchemas = Union[SaltstackCreate, GuacamoleCreate, OpenstackCreate]
UpdateSchemas = Union[SaltstackUpdate, GuacamoleUpdate, OpenstackUpdate]


class AllDatasourcesResponse(CustomBaseModel):
    '''The response listing all of the datasources of each type
    in a single response.'''
    openstack_data: Annotated[
        APIListResponse[OpenstackResponse],
        Field(..., description="The list of openstack datasources")
    ]
    guacamole_data: Annotated[
        APIListResponse[GuacamoleResponse],
        Field(..., description="The list of guacamole datasources")
    ]
    saltstack_data: Annotated[
        APIListResponse[SaltstackResponse],
        Field(..., description="The list of saltstack datasources")
    ]


class EnabledDatasourcesResponse(CustomBaseModel):
    '''The response listing all of the enabled datasources of 
    each type.'''
    openstack: Annotated[
        OpenstackResponse | None,
        Field(None, description="The enabled openstack datasource")
    ] = None
    guacamole: Annotated[
        GuacamoleResponse | None,
        Field(None, description="The enabled guacamole datasource")
    ] = None
    saltstack: Annotated[
        SaltstackResponse | None,
        Field(None, description="The enabled saltstack datasource")
    ] = None


class ConnectionTestResults(CustomBaseModel):
    '''The response of a connection test of a datasource'''
    success: Annotated[bool, Field(
        ...,
        description='Whether the connection test was successful'
    )]
    message: Annotated[str, Field(
        ...,
        description='The result of the operation'
    )]
    error: Annotated[str | None, Field(
        ...,
        description='The error message if the operation failed'
    )]


class DatasourceDeleteData(CustomBaseModel):
    '''The meta data of a datasource deleted returned in the response'''
    datasource_type: Annotated[str, Field(
        ...,
        description='The type of the datasource deleted'
    )]
    username: Annotated[str, Field(
        ...,
        description='The username of the datasource deleted'
    )]
    was_enabled: Annotated[bool, Field(
        ...,
        description='Whether the datasource was enabled before deletion'
    )]


class DatasourceDeleteResponse(CustomBaseModel):
    '''The response for a datasource when deleted'''
    success: Annotated[bool, Field(
        ...,
        description='Whether the operation was successful'
    )]
    message: Annotated[str, Field(
        ...,
        description='Describes the result of the operation'
    )]
    data: Annotated[DatasourceDeleteData, Field(
        ...,
        description='The meta data of the datasource deleted'
    )]
