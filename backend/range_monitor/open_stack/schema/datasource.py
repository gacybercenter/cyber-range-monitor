from typing import Annotated, Literal

from pydantic import Field

from range_monitor.datasource.schema import (
    DataSourceCreateBody,
    DatasourceListResponse,
    DataSourceResponse,
    DatasourceUpdateBody,
)
from range_monitor.datasource.types import DataSourceType

AuthURL = Annotated[
    str,
    Field(
        description='The authentication URL for OpenStack',
        min_length=1,
        max_length=255,
    ),
]
UserDomainName = Annotated[
    str,
    Field(
        description='The user domain name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]
RegionName = Annotated[
    str,
    Field(
        description='The region name for OpenStack',
        min_length=1,
        max_length=64,
    ),
]
APIVersion = Annotated[
    str,
    Field(
        description='The API version for OpenStack',
        min_length=1,
        max_length=8,
    ),
]


ProjectName = Annotated[
    str,
    Field(
        description='The project name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]

ProjectID = Annotated[
    str,
    Field(
        description='The project ID for OpenStack',
        min_length=1,
        max_length=64,
    ),
]

ProjectDomainName = Annotated[
    str,
    Field(
        description='The project domain name for OpenStack',
        min_length=1,
        max_length=255,
    ),
]

class OpenStackResponse(DataSourceResponse):
    type: Literal[DataSourceType.OPENSTACK] = DataSourceType.OPENSTACK
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    auth_url: AuthURL

    project_name: ProjectName | None = None
    project_id: ProjectID | None = None
    project_domain_name: ProjectDomainName | None = None



class CreateOpenStackBody(DataSourceCreateBody):
    type: Literal[DataSourceType.OPENSTACK] = DataSourceType.OPENSTACK
    auth_url: AuthURL
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    project_name: ProjectName | None = None
    project_id: ProjectID | None = None
    project_domain_name: ProjectDomainName | None = None

    def has_one_project_parameters(self) -> bool:
        return bool(self.project_name or self.project_id or self.project_domain_name)

class UpdateOpenStackBody(DatasourceUpdateBody):
    auth_url: AuthURL | None = None
    user_domain_name: UserDomainName | None = None
    region_name: RegionName | None = None
    identity_api_version: APIVersion | None = None
    project_name: ProjectName | None = None
    project_id: ProjectID | None = None
    project_domain_name: ProjectDomainName | None = None


class OpenStackListResponse(DatasourceListResponse):
    data: list[OpenStackResponse] = Field(
        ...,
        description='List of OpenStack data sources on the current page'
    )