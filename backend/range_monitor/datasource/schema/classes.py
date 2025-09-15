
from datetime import datetime

from pydantic import Field, model_validator

from range_monitor.datasource.schema.annotations import (
    AdapterID,
    AdapterPassword,
    AdapterUsername,
    APIVersion,
    AuthURL,
    GuacamoleEndpoint,
    GuacamoleSource,
    ProjectDomainName,
    ProjectID,
    ProjectName,
    RegionName,
    SaltstackEndpoint,
    SaltStackHostname,
    UserDomainName,
)
from range_monitor.schema import PaginatedList, RequestBody, ResponseModel


class DatasourceSchema(ResponseModel):
    id: AdapterID
    username: AdapterUsername
    enabled: bool = Field(..., description='Whether this adapter is enabled')
    created_at: datetime
    updated_at: datetime



class GuacamoleDatasource(DatasourceSchema):
    host: GuacamoleEndpoint
    data_source: GuacamoleSource

class OpenStackDatasource(DatasourceSchema):
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    auth_url: AuthURL

    project_name: ProjectName | None = None
    project_id: ProjectID | None = None
    project_domain_name: ProjectDomainName | None = None


class SaltStackDatasource(DatasourceSchema):
    hostname: SaltStackHostname
    endpoint: SaltstackEndpoint


class CreateDatasource(RequestBody):
    username: AdapterUsername
    password: AdapterPassword


# -- create schemas ---
class CreateOpenStackBody(CreateDatasource):
    project_id: ProjectID | None = None
    project_name: ProjectName | None = None
    project_domain_name: ProjectDomainName | None = None
    user_domain_name: UserDomainName
    region_name: RegionName
    identity_api_version: APIVersion
    auth_url: AuthURL

    @model_validator(mode='after')
    def check_project_fields(self):
        if (
            not self.project_id
            and not self.project_name
            and not self.project_domain_name
        ):
            raise ValueError(
                'At least one of project_id, project_name, or '
                'project_domain_name must be provided'
            )

        return self

class CreateGuacamoleBody(CreateDatasource):
    data_source: GuacamoleSource
    host: GuacamoleEndpoint

class CreateSaltStackSchema(CreateDatasource):
    hostname: SaltStackHostname
    endpoint: SaltstackEndpoint


class UpdateDatasource(RequestBody):
    username: AdapterUsername | None = None
    password: AdapterPassword | None = None


class UpdateOpenStackBody(UpdateDatasource):
    project_id: ProjectID | None = None
    project_name: ProjectName | None = None
    project_domain_name: ProjectDomainName | None = None
    user_domain_name: UserDomainName | None = None
    region_name: RegionName | None = None
    identity_api_version: APIVersion | None = None
    auth_url: AuthURL | None = None

class UpdateGuacamoleBody(UpdateDatasource):
    data_source: GuacamoleSource | None = None
    host: GuacamoleEndpoint | None = None

class UpdateSaltStackBody(UpdateDatasource):
    hostname: SaltStackHostname | None = None
    endpoint: SaltstackEndpoint | None = None

class GuacamolePage(PaginatedList[GuacamoleDatasource]):
    data: list[GuacamoleDatasource]


class OpenStackPage(PaginatedList[OpenStackDatasource]):
    data: list[OpenStackDatasource]

class SaltStackPage(PaginatedList[SaltStackDatasource]):
    data: list[SaltStackDatasource]


class ConnectionTestResponse(ResponseModel):
    success: bool
    is_enabled: bool
    error_message: str | None = None
    datasource_id: AdapterID | None = None