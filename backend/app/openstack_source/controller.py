
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession


from app.extensions.datasources.controller import DatasourceController

from app.extensions.datasources.errors import (
    HTTPDatasourceConnectionFailed, NoEnabledDatasourceError
)


from app.core.errors.http_errors import HTTPInvalidRequestData
from .model import OpenstackSource
from .schema import (
    OpenstackAuthSchema,
    OpenstackListResponse,
    OpenstackProtectedRead,
    OpenstackConnectionConfig
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

    async def connect_args(self, openstack: OpenstackSource) -> OpenstackConnectionConfig:
        auth_schema = OpenstackAuthSchema.model_validate(openstack)
        auth_schema.password = await self.read_datasource_password(openstack)
        return OpenstackConnectionConfig(
            region_name=openstack.region_name,
            auth=auth_schema,
            identity_api_version=openstack.identity_api_version
        )

    async def create_connection(self, connect_args: OpenstackConnectionConfig) -> connection.Connection:
        connect_init = connect_args.model_dump(exclude_none=True)
        return connection.Connection(**connect_init)

    async def connect(self, openstack: OpenstackConnectionConfig) -> connection.Connection:
        '''creates a connection to the Openstack datasource and returns the connection object
        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to
        Returns:
            connection.Connection -- the openstack connection object
        '''
        try:
            conn = await self.create_connection(openstack)
            conn.authorize()
            return conn
        except SDKException as e:
            raise HTTPDatasourceConnectionFailed(str(e.message))

    async def connect_enabled(self) -> connection.Connection:
        '''attempts to connect to the enabled Openstack datasource

        Raises:
            NoEnabledDatasourceError: if no datasource is enabled

        Returns:
            connection.Connection -- the connection object
        '''
        enabled_source: OpenstackSource | None = await self.get_enabled_source()
        if not enabled_source:
            raise NoEnabledDatasourceError(
                'Error: Could not connect to Openstack, no datasource is enabled'
            )
        connect_args = await self.connect_args(enabled_source)
        return await self.connect(connect_args)

    async def test_connection(self, conn: connection.Connection) -> tuple[bool, Optional[str]]:
        '''tests the connection to the Openstack datasource by it's ID and 
        returns a tuple of a boolean and an optional error message

        Arguments:
            id {int} -- the id of the datasource to test

        Returns:
            tuple[bool, Optional[str]] -- whether the connection was successful and 
            an optional error message
        '''
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

    async def get_all_sources(self) -> OpenstackListResponse:
        '''returns a list of all the Openstack datasources

        Returns:
            OpenstackListResponse -- the response model
        '''
        openstack_sources = await super().get_all_sources()
        list_response = OpenstackListResponse.from_list(openstack_sources)
        return list_response

    async def test_enabled_source_connection(self) -> tuple[bool, Optional[str]]:
        '''tests the connection to the enabled Openstack datasource

        Returns:
            tuple[bool, Optional[str]] -- whether the connection was successful and 
            an optional error message
        '''

        conn = await self.connect_enabled()
        try:
            conn.authorize()
        except SDKException as e:
            return False, str(e.message)
        return True, None

    async def create_datasource(self, obj_in: dict) -> OpenstackSource:
        '''ensures that either the project_id or project_name is provided
        before creating the datasource
        Arguments:
            obj_in {dict} -- the datasource data

        Raises:
            HTTPInvalidRequestData: if neither project_id or project_name is provided
        Returns:
            OpenstackSource -- the created datasource
        '''
        if not obj_in.get('project_id') and not obj_in.get('project_name'):
            raise HTTPInvalidRequestData(
                'Either project_id or project_name must be provided'
            )
        return await super().create_datasource(obj_in)  # type: ignore

    async def serialize_enabled(self) -> OpenstackProtectedRead | None:
        '''returns the enabled Openstack datasource with the password field included

        Returns:
            OpenstackProtectedRead | None -- the protected model
        '''
        enabld_src: OpenstackSource | None = await self.get_enabled_source()
        if not enabld_src:
            return None
        return await self.protected_read(enabld_src.id)
