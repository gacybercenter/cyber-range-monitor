from pydantic import (
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
    password: str
    enabled: bool


class DatasourceCreateBase(BaseModel):
    username: LimitedStr
    password: LimitedStr
    enabled: bool = Field(default=False)


class DatasourceUpdateBase(BaseModel):
    username: Optional[LimitedStr] = None
    password: Optional[LimitedStr] = None
    enabled: Optional[bool] = None


class GuacRead(DatasourceReadBase):
    datasource: LimitedStr
    endpoint: HttpUrl


class GuacCreate(DatasourceCreateBase):
    datasource: LimitedStr
    endpoint: HttpUrl


class GuacUpdate(DatasourceUpdateBase):
    datasource: Optional[LimitedStr] = None
    endpoint: Optional[HttpUrl] = None


class OpenstackRead(DatasourceReadBase):
    auth_url: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    project_domain_name: str
    user_domain_name: str
    region_name: str
    identity_api_version: str

    model_config = ConfigDict(from_attributes=True)


class OpenstackCreate(DatasourceCreateBase):
    auth_url: HttpUrl

    project_id: Optional[LimitedStr] = None
    project_name: Optional[LimitedStr] = None
    project_domain_name: Optional[LimitedStr] = None

    user_domain_name: LimitedStr
    region_name: Region
    identity_api_version: Id_Api_Version


class OpenstackUpdate(DatasourceUpdateBase):
    auth_url: Optional[HttpUrl] = None
    project_id: Optional[LimitedStr] = None
    project_name: Optional[LimitedStr] = None
    project_domain_name: Optional[LimitedStr] = None
    user_domain_name: Optional[LimitedStr] = None
    region_name: Optional[LimitedStr] = None
    identity_api_version: Optional[Id_Api_Version] = None


class SaltstackRead(DatasourceReadBase):
    endpoint: HttpUrl
    hostname: str


class SaltstackCreate(DatasourceCreateBase):
    endpoint: HttpUrl
    hostname: Hostname


class SaltstackUpdate(DatasourceUpdateBase):
    endpoint: Optional[HttpUrl] = None
    hostname: Optional[Hostname] = None


def main() -> None:
    guac = GuacCreate(
        username='admin',
        password='admin',
        enabled=True,
        datasource='guacamole',
        endpoint='http://localhost:8080/guacamole' # type: ignore
    )
    print(guac.model_dump(mode='json'))


if __name__ == '__main__':
    main()
