from typing import Annotated

from pydantic import Field, model_validator

from range_monitor.schema.http import PageModel
from range_monitor.sources.schemas.base import (
    CreateDatasource,
    DatasourceSchema,
    PatchDatasource,
)

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


class OpenstackSchema(DatasourceSchema):
    auth_url: AuthURL
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    project_id: ProjectID | None = None
    project_name: ProjectName | None = None
    project_domain_name: ProjectDomainName | None = None


class CreateOpenstackBody(CreateDatasource):
    auth_url: AuthURL
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    project_id: ProjectID | None = None
    project_name: ProjectName | None = None
    project_domain_name: ProjectDomainName | None = None

    @model_validator(mode='before')
    def ensure_project_id_or_name(cls, values):
        has_project_id = bool(values.get('project_id'))
        has_project_name = bool(values.get('project_name'))
        has_project_domain = bool(values.get('project_domain_name'))

        if not has_project_id and not has_project_name:
            raise ValueError(
                "Must provide either 'project_id' or both 'project_name' and "
                "'project_domain_name'"
            )

        if has_project_id and has_project_name:
            raise ValueError(
                "Cannot provide both 'project_id' and 'project_name'. "
                "Choose one method."
            )

        if has_project_name and not has_project_domain:
            raise ValueError(
                "When using 'project_name', 'project_domain_name' is also required"
            )

        if has_project_domain and not has_project_name:
            raise ValueError(
                "When using 'project_domain_name', 'project_name' is also required"
            )

        return values


class PatchOpenStackBody(PatchDatasource):
    auth_url: AuthURL | None = None
    user_domain_name: UserDomainName | None = None
    region_name: RegionName | None = None
    identity_api_version: APIVersion | None = None
    project_id: ProjectID | None = None
    project_name: ProjectName | None = None
    project_domain_name: ProjectDomainName | None = None


class OpenstackPage(PageModel[OpenstackSchema]):
    data: list[OpenstackSchema]
