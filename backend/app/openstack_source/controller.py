
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession


from app.extensions.datasources.controller import DatasourceController

from app.extensions.datasources.errors import NoEnabledDatasourceError

from app.extensions.datasources.model import DatasourceMixin

from app.core.errors.http_errors import  HTTPInvalidRequestData
from .model import OpenstackSource
from .schema import (
    OpenstackAuthSchema,
    OpenstackListResponse,
    OpenstackProtectedRead,
)

from openstack import connection
from openstack.exceptions import SDKException


class OpenstackController(DatasourceController):
    '''The controller for the Openstack datasource'''

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OpenstackSource, db)

    async def get_auth_dict(self, openstack: OpenstackSource) -> dict:
        auth_schema = OpenstackAuthSchema.model_validate(openstack)
        return auth_schema.model_dump(exclude_none=True, exclude_unset=True)

    async def create_connection(self, openstack: OpenstackSource, src_password: str) -> connection.Connection:
        '''creates a connection to the Openstack datasource and returns the connection object
        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to
        Returns:
            connection.Connection -- the openstack connection object
        '''
        conn_auth = await self.get_auth_dict(openstack)
        conn_auth['password'] = src_password
        return connection.Connection(
            region_name=openstack.region_name,
            auth=conn_auth,
            identity_api_version=openstack.identity_api_version
        )

    async def test_connection(self, source_id: int) -> tuple[bool, Optional[str]]:
        '''tests the connection to the Openstack datasource by it's ID and 
        returns a tuple of a boolean and an optional error message

        Arguments:
            id {int} -- the id of the datasource to test

        Returns:
            tuple[bool, Optional[str]] -- whether the connection was successful and 
            an optional error message
        '''
        conn = await self.connect_by_id(source_id)
        try:
            conn.authorize()
        except SDKException as e:
            return False, str(e.message)
        return True, None

    async def protected_read(self, id: int) -> OpenstackProtectedRead:
        '''returns the OpenstackRead schema with the password
        field included

        Arguments:
            id {int} -- the id of the datasource to read

        Returns:
            OpenstackRead -- the protected model
        '''
        openstack_src, password = await super().protected_read(id)
        protected_schema = OpenstackProtectedRead.to_model(openstack_src)
        protected_schema.password = password
        return protected_schema

    async def connect_by_id(self, source_id: int) -> connection.Connection:
        '''connects to the Openstack datasource by its id and returns the connection object

        Arguments:
            source_id {int} -- the id of the datasource

        Returns:
            connection.Connection -- the openstack connection obj
        '''
        openstack_src, password = await super().protected_read(source_id)
        return await self.create_connection(openstack_src, password)

    async def get_all_sources(self) -> OpenstackListResponse:
        '''returns a list of all the Openstack datasources

        Returns:
            OpenstackListResponse -- the response model
        '''
        openstack_sources = await super().get_all_sources()
        list_response = OpenstackListResponse.from_list(openstack_sources)
        return list_response

    async def connect_enabled_datasource(self) -> connection.Connection:
        enabled_source: OpenstackSource = await self.get_enabled_source()  # type: ignore
        if not enabled_source:
            raise NoEnabledDatasourceError()
        enabled_pwd = await self.read_datasource_password(enabled_source)
        connection = await self.create_connection(enabled_source, enabled_pwd)
        return connection

    async def test_enabled_source_connection(self) -> tuple[bool, Optional[str]]:
        '''tests the connection to the enabled Openstack datasource

        Returns:
            tuple[bool, Optional[str]] -- whether the connection was successful and 
            an optional error message
        '''
        conn = await self.connect_enabled_datasource()
        try:
            conn.authorize()
        except SDKException as e:
            return False, str(e.message)
        return True, None

    async def create_datasource(self, obj_in: dict) -> OpenstackSource:
        if not obj_in.get('project_id') and not obj_in.get('project_name'):
            raise HTTPInvalidRequestData(
                'Either project_id or project_name must be provided'
            )

        return await super().create_datasource(obj_in)  # type: ignore
