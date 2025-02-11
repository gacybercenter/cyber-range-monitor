from pydantic import (
    AnyUrl,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
)
from typing import Optional, Annotated

LimitedStr = Annotated[str, StringConstraints(min_length=1, max_length=255)]

Id_Api_Version = Annotated[str, StringConstraints(
    min_length=1,
    max_length=3,
    pattern=r"^(2.0|3)$"
)]

Region = Annotated[str, StringConstraints(
    min_length=1,
    max_length=50,
)]

Hostname = Annotated[str, StringConstraints(
    min_length=1,
    max_length=253
)]


class DatasourceReadBase(BaseModel):
    id: int
    username: str
    enabled: bool


class DatasourceProtectedRead(DatasourceReadBase):
    password: str


class DatasourceCreateBase(BaseModel):
    username: Annotated[
        LimitedStr,
        Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        LimitedStr,
        Field(..., description="The password for the datasource")
    ]
    enabled: Annotated[
        bool,
        Field(..., description="Whether the datasource is enabled by default")
    ]


class DatasourceUpdateBase(BaseModel):
    username: Annotated[
        Optional[LimitedStr],
        Field(..., description="The username for the datasource")
    ]
    password: Annotated[
        Optional[LimitedStr],
        Field(..., description="The password for the datasource")
    ]
    enabled: Optional[bool] = None


class GuacamoleRead(DatasourceReadBase):
    datasource: Annotated[
        LimitedStr,
        Field(..., description="The name of the Guacamole datasource")
    ]
    endpoint: Annotated[
        AnyUrl,
        Field(..., description="The URL for the Guacamole datasource")
    ]


class GuacamoleCreate(DatasourceCreateBase):
    datasource: Annotated[
        LimitedStr,
        Field(..., description="The name of the Guacamole datasource")
    ]
    endpoint: Annotated[
        AnyUrl,
        Field(..., description="The URL for the Guacamole datasource")
    ]


class GuacamoleUpdate(DatasourceUpdateBase):
    datasource: Annotated[
        Optional[LimitedStr],
        Field(
            None,
            description="The name of the Guacamole datasource"
        )
    ]
    endpoint: Annotated[
        Optional[HttpUrl],
        Field(
            None,
            description="The URL for the Guacamole datasource"
        )
    ]


class OpenstackRead(DatasourceReadBase):
    auth_url: Annotated[
        str,
        Field(
            ...,
            description="The URL for the Openstack authentication"
        )
    ]
    project_id: Annotated[
        Optional[str],
        Field(
            None,
            description="The project ID for the Openstack authentication"
        )
    ]
    project_name: Annotated[
        Optional[str],
        Field(
            None,
            description="The project name for the Openstack authentication"
        )
    ]
    project_domain_name: Annotated[
        str,
        Field(
            ...,
            description="The project domain name for the Openstack authentication"
        )
    ]
    user_domain_name: Annotated[
        str,
        Field(
            ...,
            description="The user domain name for the Openstack authentication"
        )
    ]
    region_name: Annotated[
        str,
        Field(
            ...,
            description="The region name for the Openstack authentication"
        )
    ]
    identity_api_version: Annotated[
        str,
        Field(
            ...,
            description="The identity API version for the Openstack authentication"
        )
    ]

    model_config = ConfigDict(from_attributes=True)


class OpenstackCreate(DatasourceCreateBase):
    auth_url: Annotated[
        HttpUrl,
        Field(
            ...,
            description="The URL for the Openstack authentication"
        )
    ]

    project_id: Annotated[
        Optional[str],
        Field(
            None,
            description="The project ID for the Openstack authentication"
        )
    ]
    project_name: Annotated[
        Optional[str],
        Field(
            None,
            description="The project name for the Openstack authentication"
        )
    ]
    project_domain_name: Annotated[
        str,
        Field(
            ...,
            description="The project domain name for the Openstack authentication"
        )
    ]
    user_domain_name: Annotated[
        LimitedStr,
        Field(
            ...,
            description="The user domain name for the Openstack authentication"
        )
    ]
    region_name: Annotated[
        Region,
        Field(
            ...,
            description="The region name for the Openstack authentication"
        )
    ]
    identity_api_version: Annotated[
        Id_Api_Version,
        Field(
            ...,
            description="The identity API version for the Openstack authentication"
        )
    ]


class OpenstackUpdate(DatasourceUpdateBase):
    auth_url: Annotated[
        Optional[HttpUrl],
        Field(
            ...,
            description="The URL for the Openstack authentication"
        )
    ]

    project_id: Annotated[
        Optional[str],
        Field(
            None,
            description="The project ID for the Openstack authentication"
        )
    ]
    project_name: Annotated[
        Optional[str],
        Field(
            None,
            description="The project name for the Openstack authentication"
        )
    ]
    project_domain_name: Annotated[
        Optional[str],
        Field(
            ...,
            description="The project domain name for the Openstack authentication"
        )
    ]
    user_domain_name: Annotated[
        Optional[LimitedStr],
        Field(
            ...,
            description="The user domain name for the Openstack authentication"
        )
    ]
    region_name: Annotated[
        Optional[Region],
        Field(
            ...,
            description="The region name for the Openstack authentication"
        )
    ]
    identity_api_version: Annotated[
        Optional[Id_Api_Version],
        Field(
            ...,
            description="The identity API version for the Openstack authentication"
        )
    ]


class SaltstackRead(DatasourceReadBase):
    endpoint: Annotated[
        str,
        Field(
            ...,
            description="The endpoint for the Saltstack datasource"
        )
    ]
    hostname: Annotated[
        str,
        Field(
            ...,
            description="The hostname for the Saltstack datasource"
        )
    ]


class SaltstackCreate(DatasourceCreateBase):
    endpoint: Annotated[
        HttpUrl,
        Field(
            ...,
            description="The endpoint for the Saltstack datasource"
        )
    ]
    hostname: Annotated[
        Hostname,
        Field(
            ...,
            description="The hostname for the Saltstack datasource"
        )
    ]


class SaltstackUpdate(DatasourceUpdateBase):
    endpoint: Annotated[
        Optional[HttpUrl],
        Field(
            None,
            description="The endpoint for the Saltstack datasource"
        )
    ]
    hostname: Annotated[
        Optional[Hostname],
        Field(
            None,
            description="The endpoint for the Saltstack datasource"
        )
    ]


def main() -> None:
    Guacamole = GuacamoleCreate(
        username='admin',
        password='admin',
        enabled=True,
        datasource='Guacamoleamole',
        endpoint='http://localhost:8080/Guacamoleamole'  # type: ignore
    )
    print(Guacamole.model_dump(mode='json'))


if __name__ == '__main__':
    main()
