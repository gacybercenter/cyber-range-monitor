from typing import Annotated, List, Self
from pydantic import ConfigDict, Field

from ..interface.base_schema import (
    DatasourceOptions,
    DatasourceConnectionArgs,
    DatasourceResponse,
    DatasourceList,
    CustomBaseModel,
    DatasourceCreateBody,
    DatasourceUpdateBody,
    FixedStr,
    RouterAnnotations,
    options_desc,
)


PROJECT_ID_DESC = "The project ID for the Openstack authentication"
PROJECT_NAME_DESC = "The project name for the Openstack authentication"
PROJECT_DOMAIN_NAME_DESC = "The project domain name for the Openstack authentication"
USER_DOMAIN_NAME_DESC = "The user domain name for the Openstack authentication"
REGION_NAME_DESC = "The region name for the Openstack authentication"
IDENTITY_API_VERSION_DESC = "The identity API version for the Openstack authentication"


ProjectName = Annotated[
    FixedStr | None,
    Field(default=None, description=PROJECT_NAME_DESC),
]

ProjectID = Annotated[
    FixedStr | None,
    Field(default=None, description=PROJECT_ID_DESC),
]

ProjectDomainName = Annotated[
    FixedStr | None,
    Field(default=None, description=PROJECT_DOMAIN_NAME_DESC),
]


class OpenstackOptions(DatasourceOptions):
    """The options for a openstack"""

    project_id: ProjectID

    project_name: ProjectName

    project_domain_name: ProjectDomainName

    user_domain_name: Annotated[FixedStr, Field(..., description=USER_DOMAIN_NAME_DESC)]

    region_name: Annotated[FixedStr, Field(..., description=REGION_NAME_DESC)]

    identity_api_version: Annotated[
        FixedStr, Field(..., description=IDENTITY_API_VERSION_DESC)
    ]


class OpenstackOptionsUpdate(DatasourceOptions):
    project_id: ProjectID
    project_name: ProjectName
    project_domain_name: ProjectDomainName

    user_domain_name: Annotated[
        FixedStr | None, Field(default=None, description=USER_DOMAIN_NAME_DESC)
    ]

    region_name: Annotated[
        FixedStr | None, Field(default=None, description=REGION_NAME_DESC)
    ]

    identity_api_version: Annotated[
        FixedStr | None, Field(default=None, description=IDENTITY_API_VERSION_DESC)
    ]


OpenStackOpts = Annotated[
    OpenstackOptions,
    Field(..., description=options_desc("openstack")),
]


class OpenstackCreateBody(DatasourceCreateBody):
    """The request body to create a new openstack datasource"""

    options: OpenStackOpts


class OpenstackUpdateBody(DatasourceUpdateBody):
    """The request body to update an openstack datasource"""

    options: Annotated[
        OpenstackOptionsUpdate | None,
        Field(None, description=options_desc("openstack")),
    ]


class OpenstackResponse(DatasourceResponse):
    """The response body for an openstack datasource"""

    options: OpenStackOpts


class OpenstackList(DatasourceList):
    """The response body for a list of openstack datasources"""

    data: Annotated[
        List[OpenstackResponse],
        Field(..., description="The list of openstack datasources"),
    ]


class OpenstackAuthParams(CustomBaseModel):
    """The "auth" dictionary parameter for an openstack connection."""

    endpoint: str  # needs to change to 'auth_url' before being passed to connection.Connection ctor
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None

    model_config = ConfigDict(from_attributes=True)


class OpenstackConnectionParams(DatasourceConnectionArgs):
    """The keyword arguments to create an openstack connection"""

    auth: Annotated[
        dict,
        Field(..., description="The auth dictionary for the Openstack connection"),
    ]
    region_name: Annotated[
        str,
        Field(..., description="The region name for the Openstack connection"),
    ]
    identity_api_version: Annotated[
        str,
        Field(..., description="The identity API version for the Openstack connection"),
    ]

    @classmethod
    def create(
        cls, *, auth: OpenstackAuthParams, region_name: str, id_api_version: str
    ) -> Self:
        """Creates an OpenstackConnectionParams object from the given parameters,
        but ensures "endpoint" attribute is renamed to "auth_url"

        Args:
            auth (OpenstackAuthParams): _the auth parameters_
            region_name (str): _the region name_
            id_api_version (str): _the api version_

        Returns:
            Self: _instance_
        """
        auth_dict = auth.serialize_exclude(exclude={"endpoint"})
        auth_dict["auth_url"] = auth.endpoint

        return cls(
            auth=auth_dict, region_name=region_name, identity_api_version=id_api_version
        )


def create_openstack_annotation() -> RouterAnnotations:
    return RouterAnnotations(
        CreateBody=OpenstackCreateBody,
        UpdateBody=OpenstackUpdateBody,
        Response=OpenstackResponse,
        ListResponse=OpenstackList,
    )
