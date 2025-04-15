
from sqlalchemy.ext.asyncio import AsyncSession

from openstack import connection
from openstack.exceptions import SDKException

from app.core.errors import HTTPBadRequestData

from app.datasource.base.controller import DatasourceController
from app.datasource.base.errors import HTTPDatasourceConnectionFailed

from .model import OpenstackSource
from .schema import (
    OpenstackAuthSchema,
    OpenstackCreate,
    OpenstackConnectionConfig,
    OpenstackRead
)


class OpenstackSourceService(DatasourceController[OpenstackSource]):
    '''The service for Openstack Datasources'''

    def __init__(self, db: AsyncSession) -> None:
        self.model = OpenstackSource
        super().__init__(db)

    async def get_openstack_auth(self, openstack: OpenstackSource) -> dict:
        '''returns the Openstack auth dictionary for the Openstack datasource

        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            dict -- the Openstack auth dictionary for the 'auth' parameter
            for an openstack connection
        '''
        auth_schema = OpenstackAuthSchema.model_validate(openstack)
        auth_schema.password = await self.read_datasource_password(openstack)
        auth_dict = auth_schema.model_dump(
            exclude_none=True,
            exclude_unset=True
        )
        auth_dict['auth_url'] = auth_schema.endpoint
        del auth_dict['endpoint']
        return auth_dict

    def _validate_schema(self, request_schema: OpenstackCreate) -> dict:
        '''Ensures either a project id or project name is provided
        since the Openstack datasource requires one of them to 
        create a connection

        Arguments:
            request_schema {OpenstackCreate} -- the request schema

        Returns:
            dict -- the serialized schema
        '''
        if not request_schema.project_id and not request_schema.project_name:
            raise HTTPBadRequestData(
                'Either Project ID or Project Name must be '
                'provided to create an Openstack datasource'
            )
        return super()._validate_schema(request_schema)

    def serialize(self, source: OpenstackSource) -> OpenstackRead:
        '''serializes the Openstack datasource to a protected read schema
        Arguments:
            source {OpenstackSource} -- the Openstack datasource to serialize
        Returns:
            OpenstackProtectedRead -- the serialized Openstack datasource
        '''
        return OpenstackRead.to_model(source)

    async def connect_args(self, source: OpenstackSource) -> OpenstackConnectionConfig:
        '''Creates the arguments / Connection Model that when passed to the Openstack connection
        will create a connection to the Openstack datasource

        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            OpenstackConnectionConfig -- the connection model 
            that represents the connection to the Openstack 
        '''
        auth = await self.get_openstack_auth(source)
        return OpenstackConnectionConfig(
            region_name=source.region_name,
            auth=auth,
            identity_api_version=source.identity_api_version
        )

    async def connect(self, source: OpenstackSource) -> connection.Connection:
        '''creates a connection to the Openstack datasource and returns the connection object
        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to
        Returns:
            connection.Connection -- the openstack connection object
        '''
        try:
            conn_args = await self.connect_args(source)
            conn = connection.Connection(**conn_args.model_dump())
            conn.authorize()
            return conn
        except SDKException as e:
            raise HTTPDatasourceConnectionFailed(str(e.message))

    async def test_datasource_connection(self, source: OpenstackSource) -> tuple[str | None, bool]:
        '''tests the connection to the Openstack datasource by it's ID and 
        returns a tuple of a boolean and an optional error message

        Arguments:
            id {int} -- the id of the datasource to test

        Returns:
            tuple[bool, Optional[str]] -- whether the connection was successful and 
            an optional error message
        '''
        try:
            conn_args = await self.connect_args(source)
            conn = connection.Connection(**conn_args.model_dump())
            conn.authorize()
        except SDKException as e:
            return str(e.message), False
        return None, True
