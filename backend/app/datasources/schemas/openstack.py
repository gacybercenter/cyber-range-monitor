from typing import Annotated

from pydantic import ConfigDict, Field, StringConstraints

from .base_schemas import (
    DatasourceCreateForm,
    DatasourceRead,
    DatasourceUpdateForm,
    LimitedStr,
)

Id_Api_Version = Annotated[
    str, StringConstraints(min_length=1, max_length=3, pattern=r"^(2.0|3)$")
]

Region = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=50,
    ),
]


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
        Field(..., description="The project domain name for the Openstack authentication"),
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

    model_config = ConfigDict(from_attributes=True)


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
        Field(..., description="The project domain name for the Openstack authentication"),
    ]
    user_domain_name: Annotated[
        LimitedStr,
        Field(..., description="The user domain name for the Openstack authentication"),
    ]
    region_name: Annotated[
        Region, Field(..., description="The region name for the Openstack authentication")
    ]
    identity_api_version: Annotated[
        Id_Api_Version,
        Field(
            ..., description="The identity API version for the Openstack authentication"
        ),
    ]


class OpenstackUpdateForm(DatasourceUpdateForm):
    """The form for updating a Openstack datasource"""

    auth_url: Annotated[
        str | None, Field(..., description="The URL for the Openstack authentication")
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
        Field(..., description="The project domain name for the Openstack authentication"),
    ]

    user_domain_name: Annotated[
        LimitedStr | None,
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
        ),
    ]
