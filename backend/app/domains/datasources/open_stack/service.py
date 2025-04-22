from sqlalchemy.ext.asyncio import AsyncSession

from openstack import connection
from openstack.exceptions import SDKException

from app.db.models import OpenstackSource

from app.core.datasources.service import DatasourceServiceABC
from app.core.errors import HTTPBadRequest


from .schema import (
    OpenstackAuthSchema,
    OpenstackConnectionArgs,
    OpenstackOptions,
    OpenstackResponse,
    OpenstackUpdateOptions,
    OpenstackCreate,
    OpenstackUpdate
)


class OpenstackSourceService(DatasourceServiceABC[
    OpenstackSource, OpenstackCreate, OpenstackUpdate
]):
    """The service for the OpenstackSource model"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(OpenstackSource, db)

    def validate_create_schema(self, req_body: dict) -> dict:
        """validates the options for the OpenstackSource datasource
        to ensure it matches the schema and includes the proper options.
        """
        options = req_body.get('options')
        if not options:
            raise HTTPBadRequest(
                "Options must be provided to create this datasource.")
        schema = OpenstackOptions.model_validate(options)
        if schema.project_id is None and schema.project_name is None:
            raise HTTPBadRequest(
                "Either project_id or project_name must be provided"
            )
        req_body['options'] = schema.serialize()
        return self._flatten_request_body(req_body)

    def validate_update_schema(self, req_body: dict) -> dict:
        """validates the options for the OpenstackSource datasource"""
        opts = req_body.get('options')
        if not opts:
            return req_body
        schema = OpenstackUpdateOptions.model_validate(opts)
        req_body['options'] = schema.serialize()
        return self._flatten_request_body(req_body)

    async def get_openstack_auth(self, openstack: OpenstackSource) -> dict:
        '''creates the Openstack auth dictionary for the Openstack datasource
        used in the "auth" parameter to create a connection object.

        Arguments:
            openstack {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            dict -- the Openstack auth dictionary for the 'auth' parameter
            for an openstack connection
        '''
        auth_schema = OpenstackAuthSchema.model_validate(openstack)
        auth_schema.password = await self.models.read_password(openstack)
        auth_dict = auth_schema.model_dump(
            exclude_none=True,
            exclude_unset=True
        )
        auth_url = auth_dict.pop('endpoint')
        if not auth_url:
            raise HTTPBadRequest(
                'Invalid datasource, no auth url / endpoint was provided'
            )

        auth_dict['auth_url'] = auth_url
        return auth_dict

    async def connect_args(self, datasource: OpenstackSource) -> dict:
        '''returns the connection arguments for the Openstack datasource.

        Arguments:
            datasource {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            dict -- the connection arguments for the Openstack datasource
        '''
        auth = await self.get_openstack_auth(datasource)
        return OpenstackConnectionArgs(
            auth=auth,
            region_name=datasource.region_name,
            identity_api_version=datasource.identity_api_version
        ).serialize()

    async def connect(self, datasource: OpenstackSource) -> connection.Connection:
        '''creates a connection to the Openstack datasource and returns the connection object

        Arguments:
            source {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            connection.Connection -- the Openstack connection object
        '''
        try:
            conn_args = await self.connect_args(datasource)
            conn = connection.Connection(**conn_args)
            conn.authorize()
            return conn
        except SDKException as e:
            raise HTTPBadRequest(
                f'Failed to connect to Openstack datasource: {e}'
            ) from e

    async def test_connection(self, source: OpenstackSource) -> tuple[str | None, bool]:
        '''tests the connection to the Openstack datasource and returns the session object

        Arguments:
            source {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            Optional[connection.Connection] -- the Openstack connection object or None if the 
            connection failed & a key error occured
        '''
        try:
            conn_args = await self.connect_args(source)
            conn = connection.Connection(**conn_args)
            conn.authorize()
        except SDKException as e:
            return str(e), False

        return None, True

    def to_response(self, datasource: OpenstackSource) -> OpenstackResponse:
        """serializes the Openstack datasource into the key word arguments to create the response model"""
        base_args_dict = self.get_base_args(datasource)
        options_schema = OpenstackOptions.to_model(datasource)
        return OpenstackResponse(
            **base_args_dict,
            options=options_schema
        )
