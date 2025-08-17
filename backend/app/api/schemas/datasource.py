from typing import Annotated

from pydantic import Field

from app.core.pydantic import FixedStr

from .interface import PageMixin, RequestSchema, ResponseSchema

DatasourceID = Annotated[
    str, Field(description='The unique identifier of the data source')
]

DatasourceUsername = Annotated[
    FixedStr, Field(description='The username for the data source connection')
]

DatasourcePassword = Annotated[
    FixedStr, Field(description='The password for the data source connection')
]

DatasourceEndpoint = Annotated[
    str,
    Field(
        description='The endpoint for the data source connection',
        min_length=5,
        max_length=256,
    ),
]

DatasourceEnabled = Annotated[
    bool, Field(description='Whether the data source is enabled or not')
]


class DataSourceModel(ResponseSchema):
    id: DatasourceID
    username: DatasourceUsername
    password: DatasourcePassword
    endpoint: DatasourceEndpoint
    enabled: DatasourceEnabled


class DataSourceCreateModel(RequestSchema):
    username: DatasourceUsername
    password: DatasourcePassword
    endpoint: DatasourceEndpoint


class DataSourceUpdateModel(RequestSchema):
    username: DatasourceUsername | None = None
    password: DatasourcePassword | None = None
    endpoint: DatasourceEndpoint | None = None


GuacamoleSource = Annotated[
    str,
    Field(
        description='The source of the Guacamole data source, e.g., "guacd"',
        min_length=1,
        max_length=50,
    ),
]


class GuacamoleDataSourceModel(DataSourceModel):
    source: GuacamoleSource


class GuacamoleCreateModel(DataSourceCreateModel):
    source: GuacamoleSource


class GuacamoleUpdateModel(DataSourceUpdateModel):
    source: GuacamoleSource | None = None


class GuacamolePage(PageMixin):
    data: list[GuacamoleDataSourceModel] = Field(
        ..., description='The list of Guacamole data sources'
    )


OpenstackDomainName = Annotated[
    FixedStr,
    Field(description='The OpenStack domain name associated with the data source'),
]
OpenstackRegion = Annotated[
    FixedStr,
    Field(description='The OpenStack region associated with the data source'),
]
OpenstackApiVersion = Annotated[
    str,
    Field(
        description='The OpenStack API version associated with the data source',
        min_length=1,
        max_length=10,
    ),
]

OpenstackProjectName = Annotated[
    str,
    Field(
        description='The OpenStack project name associated with the data source',
    ),
]
OpenstackProjectID = Annotated[
    FixedStr,
    Field(
        description='The OpenStack project ID associated with the data source',
    ),
]
OpenstackProjectDomainName = Annotated[
    FixedStr,
    Field(
        description='The OpenStack project domain name associated with the data source',
    ),
]


class OpenStackDataSourceModel(DataSourceModel):
    """Model for OpenStack data source"""

    user_domain_name: OpenstackDomainName
    region_name: OpenstackRegion
    identity_api_version: OpenstackApiVersion
    project_id: OpenstackProjectID | None = None
    project_name: OpenstackProjectName | None = None
    project_domain_name: OpenstackProjectDomainName | None = None


class OpenStackCreateModel(DataSourceCreateModel):
    user_domain_name: OpenstackDomainName
    region_name: OpenstackRegion
    identity_api_version: OpenstackApiVersion
    project_id: OpenstackProjectID | None = None
    project_name: OpenstackProjectName | None = None
    project_domain_name: OpenstackProjectDomainName | None = None


class OpenStackUpdateModel(DataSourceUpdateModel):
    user_domain_name: OpenstackDomainName | None = None
    region_name: OpenstackRegion | None = None
    identity_api_version: OpenstackApiVersion | None = None
    project_id: OpenstackProjectID | None = None
    project_name: OpenstackProjectName | None = None
    project_domain_name: OpenstackProjectDomainName | None = None


class OpenStackPage(PageMixin):
    data: list[OpenStackDataSourceModel] = Field(
        ..., description='The list of OpenStack data sources'
    )


SaltstackHostname = Annotated[
    FixedStr,
    Field(
        description='The hostname of the SaltStack data source',
        min_length=1,
        max_length=256,
    ),
]


class SaltStackDataSourceModel(DataSourceModel):
    hostname: SaltstackHostname


class SaltStackCreateModel(DataSourceCreateModel):
    hostname: SaltstackHostname


class SaltStackUpdateModel(DataSourceUpdateModel):
    hostname: SaltstackHostname | None = None


class SaltStackPage(PageMixin):
    data: list[SaltStackDataSourceModel] = Field(
        ..., description='The list of SaltStack data sources'
    )
