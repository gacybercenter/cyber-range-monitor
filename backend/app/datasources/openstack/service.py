
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


from app.datasources.base.service import DatasourceService
from .model import Openstack
from .schema import (
    OpenstackCreateForm,
    OpenstackListResponse,
    OpenstackRead,
    OpenstackUpdateForm,
)

from openstack import connection
from openstack.exceptions import SDKException


class OpenstackService(DatasourceService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Openstack, db)

    def get_auth_dict(self, openstack: Openstack) -> dict:
        auth = {
            'auth_url': openstack.auth_url,
            'username': openstack.username,
            'user_domain_name': openstack.user_domain_name,
        }
        optional_attrs = ('project_id', 'project_name', 'project_domain_name')
        for attrs in optional_attrs:
            if getattr(openstack, attrs):
                auth[attrs] = getattr(openstack, attrs)
        return auth

    async def create_connection(self, openstack: Openstack) -> connection.Connection:
        conn_auth = self.get_auth_dict(openstack)
        conn_auth['password'] = await self.read_datasource_password(openstack)
        return connection.Connection(
            region_name=openstack.region_name,
            auth=conn_auth,
            identity_api_version=openstack.identity_api_version
        )

    async def test_connection(self, id: int) -> tuple[bool, Optional[str]]:
        openstack: Openstack = await self.get_by_id(id)  # type: ignore
        conn: connection.Connection = await self.create_connection(openstack)
        try:
            conn.authorize()
        except SDKException as e:
            return False, str(e.message)
        return True, None

    
    
    
    
    
    