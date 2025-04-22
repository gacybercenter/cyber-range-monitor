from typing import Annotated


from pydantic import BaseModel, ConfigDict, Field

from app.core.datasources.schema import (
    DatasourceOptions,
    DatasourceOptionsUpdate,
    DatasourceConnectionArgs,
    DatasourceRequest,
    DatasourceResponse,
    DatasourceUpdate
)


class OpenstackOptions(DatasourceOptions):
    '''The options for a openstack'''
    project_id: Annotated[
        str | None,
        Field(None, description="The project ID for the Openstack authentication"),
    ]

    project_name: Annotated[
        str | None,
        Field(None, description="The project name for the Openstack authentication"),
    ]

    project_domain_name: Annotated[
        str,
        Field(
            ..., description="The project domain name for the Openstack authentication"
        ),
    ]

    user_domain_name: Annotated[
        str,
        Field(..., description="The user domain name for the Openstack authentication"),
    ]

    region_name: Annotated[
        str, Field(..., description="The region name for the Openstack authentication")
    ]

    identity_api_version: Annotated[
        str,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        )
    ]
    


class OpenstackUpdateOptions(DatasourceOptionsUpdate):
    '''The options for openstack as optional arguments'''
    project_id: Annotated[
        str | None,
        Field(None, description="The project ID for the Openstack authentication"),
    ] = None

    project_name: Annotated[
        str | None,
        Field(None, description="The project name for the Openstack authentication"),
    ] = None

    project_domain_name: Annotated[
        str | None,
        Field(
            ..., description="The project domain name for the Openstack authentication"
        ),
    ] = None

    user_domain_name: Annotated[
        str | None,
        Field(..., description="The user domain name for the Openstack authentication"),
    ] = None

    region_name: Annotated[
        str | None,
        Field(..., description="The region name for the Openstack authentication"),
    ] = None

    identity_api_version: Annotated[
        str | None,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        )
    ] = None

class OpenstackCreate(DatasourceRequest[OpenstackOptions]):
    '''The request body to create a new openstack datasource'''
    pass

class OpenstackUpdate(DatasourceUpdate[OpenstackUpdateOptions]):
    '''The request body to update an openstack datasource'''
    pass

class OpenstackResponse(DatasourceResponse[OpenstackOptions]):
    '''The response body for an openstack datasource'''
    pass

class OpenstackListResponse(DatasourceResponse[OpenstackOptions]):
    '''The response body for a list of openstack datasources'''
    pass

class OpenstackAuthSchema(BaseModel):
    '''The "auth" dictionary parameter for an openstack connection.'''
    endpoint: str  # needs to change to 'auth_url' before being passed to connection.Connection ctor
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class OpenstackConnectionArgs(DatasourceConnectionArgs):
    '''The keyword arguments to create an openstack connection'''
    auth: dict  # dict must match OpenstackAuthSchema signature
    region_name: str
    identity_api_version: str
