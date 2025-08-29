
from typing import TypedDict

from openstack import connection
from openstack.exceptions import SDKException
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.errors import HTTPUnprocessableEntity

from .repo import OpenStackRepo


class OpenStackAuth(TypedDict):
    auth_url: str  # 'endpoint'
    username: str
    password: str
    user_domain_name: str

    project_id: str | None
    project_name: str | None
    project_domain_name: str | None

class OpenstackParams(TypedDict):
    auth: OpenStackAuth
    region_name: str | None
    identity_api_version: str | None





class OpenStackConnectionAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self.repo: OpenStackRepo = OpenStackRepo(session)

    def prepare_params(self, raw_orm: dict) -> OpenstackParams:
        auth = OpenStackAuth(
            auth_url=raw_orm['endpoint'],
            username=raw_orm['username'],
            password=raw_orm['password'],
            user_domain_name=raw_orm['user_domain_name'],
            project_id=raw_orm.get('project_id'),
            project_name=raw_orm.get('project_name'),
            project_domain_name=raw_orm.get('project_domain_name'),
        )
        return OpenstackParams(
            auth=auth,
            region_name=raw_orm['region_name'],
            identity_api_version=raw_orm['identity_api_version'],
        )

    async def make_connection(self, raw_orm: dict) -> connection.Connection | None:
        connection_kwrags = self.prepare_params(raw_orm)
        try:
            conn = connection.Connection(**connection_kwrags)
            conn.authorize()
            return conn
        except SDKException:
            return None

    async def test_connection(self, datasource_id: str | None = None) -> bool:

        params = await self.repo.get_connection_params(datasource_id)
        if not params:
            return False
        return await self.make_connection(params) is not None

    def _invalid_datasource(self) -> HTTPUnprocessableEntity:
        raise HTTPUnprocessableEntity(
            'The enabled OpenStack datasource is not set or is invalid.'
        )

    async def connect(self) -> connection.Connection:
        if not (params := await self.repo.get_connection_params()):
            raise self._invalid_datasource()

        if not (conn := await self.make_connection(params)):
            raise self._invalid_datasource()

        return conn