from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from typing import Annotated

from app.datasource.base.schema import (
    DatasourceConnectionModel,
    DatasourceReadModel,
    DatasourceCreateModel,
    DatasourceUpdateModel,
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
    max_length=50
)]


class OpenstackRead(DatasourceReadModel):
    """A Openstack datasource schema from the DB"""

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


class OpenstackCreate(DatasourceCreateModel):
    """The form for creating a new Openstack datasource"""

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


class OpenstackUpdate(DatasourceUpdateModel):
    """The form for updating a Openstack datasource"""

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
        FixedStr | None,
        Field(..., description="The user domain name for the Openstack authentication"),
    ] = None

    region_name: Annotated[
        Region | None,
        Field(..., description="The region name for the Openstack authentication"),
    ] = None

    identity_api_version: Annotated[
        Id_Api_Version | None,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        )
    ] = None


class OpenstackAuthSchema(BaseModel):
    '''The "auth" dictionary parameter for an openstack connection.'''
    endpoint: str
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
    auth: dict
    region_name: str
    identity_api_version: str
