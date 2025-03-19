from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from typing import Annotated

from app.extensions.datasources.schema import (
    DatasourceConnectionModel,
    DatasourceRead,
    DatasourceCreateForm,
    DatasourceUpdateForm,
    DatasourceListResponse,
    FixedStr,
    ConnectionTestResult
)


Id_Api_Version = Annotated[str, StringConstraints(
    min_length=1,
    max_length=3,
    pattern=r"^(2.0|3)$"
)]

Region = Annotated[str, StringConstraints(
    min_length=1,
    max_length=50,
)]


class OpenstackRead(DatasourceRead):
    """A Openstack datasource schema from the DB"""

    auth_url: Annotated[
        str, Field(..., description="The URL for the Openstack authentication")
    ]
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
        ),
    ]


class OpenstackCreateForm(DatasourceCreateForm):
    """The form for creating a new Openstack datasource"""

    auth_url: Annotated[
        str, Field(..., description="The URL for the Openstack authentication")
    ]

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
        FixedStr,
        Field(..., description="The user domain name for the Openstack authentication"),
    ]

    region_name: Annotated[
        Region,
        Field(..., description="The region name for the Openstack authentication"),
    ]

    identity_api_version: Annotated[
        Id_Api_Version,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        )
    ]


class OpenstackUpdateForm(DatasourceUpdateForm):
    """The form for updating a Openstack datasource"""

    auth_url: Annotated[
        str | None, Field(
            ...,
            description="The URL for the Openstack authentication"
        )
    ]

    project_id: Annotated[
        str | None,
        Field(None, description="The project ID for the Openstack authentication"),
    ]

    project_name: Annotated[
        str | None,
        Field(None, description="The project name for the Openstack authentication"),
    ]

    project_domain_name: Annotated[
        str | None,
        Field(
            ..., description="The project domain name for the Openstack authentication"
        ),
    ]

    user_domain_name: Annotated[
        FixedStr | None,
        Field(..., description="The user domain name for the Openstack authentication"),
    ]

    region_name: Annotated[
        Region | None,
        Field(..., description="The region name for the Openstack authentication"),
    ]

    identity_api_version: Annotated[
        Id_Api_Version | None,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        )
    ]


class OpenstackListResponse(DatasourceListResponse[OpenstackRead]):
    data: list[OpenstackRead]


class OpenstackProtectedRead(OpenstackRead):
    """A Openstack datasource schema with protected fields"""
    password: Annotated[
        str,
        Field(..., description="The password for the Openstack datasource"),
    ]


class OpenstackAuthSchema(BaseModel):
    '''The "auth" dictionary parameter for an openstack connection.'''
    auth_url: str
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None

    model_config = ConfigDict(
        from_attributes=True
    )


class OpenstackConnectionResults(ConnectionTestResult):

    @classmethod
    def create(cls, result: bool, err: str | None) -> 'OpenstackConnectionResults':
        msg = 'Successfully connected to the Openstack API'
        if not result:
            msg = 'Connection Attempt Failed, could not connect to the Openstack API'
        return cls(
            message=msg,
            success=result,
            error=err
        )

class OpenstackConnectionConfig(DatasourceConnectionModel):
    auth: OpenstackAuthSchema
    region_name: str
    identity_api_version: str

    





