from sqlalchemy.ext.asyncio import AsyncSession

from openstack import connection
from openstack.exceptions import SDKException

from range_monitor.common.errors import HTTPBadRequest

from ..interface.source_service_abc import DatasourceServiceABC
from .model import OpenstackSource
from .schema import (
    OpenstackAuthParams,
    OpenstackConnectionParams,
    OpenstackOptions,
    OpenstackResponse,
    OpenstackCreateBody,
)


class OpenstackSourceService(DatasourceServiceABC[OpenstackSource, OpenstackResponse]):
    """The service for the OpenstackSource model"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(datasource_type='openstack', model=OpenstackSource, db=db)

    def validate_create_schema(
        self, schema: OpenstackCreateBody
    ) -> OpenstackCreateBody:
        """validates the options for the OpenstackSource datasource
        to ensure it matches the schema and includes the proper options.
        Arguments:
            schema {OpenstackCreate} -- the request body to create a new Openstack datasource
        Returns:
            OpenstackCreate -- the validated request body
        """
        opts = schema.options
        if opts.project_id is None and opts.project_name is None:
            raise HTTPBadRequest(
                'Either project_id or project_name must be provided, both cannot be omitted'
            )
        return schema

    async def connect_args(self, datasource: OpenstackSource) -> dict:
        """returns the connection arguments for the Openstack datasource.

        Arguments:
            datasource {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            dict -- the connection arguments for the Openstack datasource
        """
        auth = OpenstackAuthParams.convert(datasource)
        auth.password = await self.models.read_password(datasource)
        params = OpenstackConnectionParams.create(
            auth=auth,
            region_name=datasource.region_name,
            id_api_version=datasource.identity_api_version,
        )

        return params.serialize()

    async def connect(self, datasource: OpenstackSource) -> connection.Connection:
        """creates a connection to the Openstack datasource and returns the connection object

        Arguments:
            source {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            connection.Connection -- the Openstack connection object
        """
        try:
            conn_args = await self.connect_args(datasource)s
            conn = connection.Connection(**conn_args)
            conn.authorize()
            return conn
        except SDKException as e:
            raise HTTPBadRequest(
                f'Failed to connect to Openstack datasource: {e}'
            ) from e

    async def test_connection(self, source: OpenstackSource) -> tuple[str | None, bool]:
        """tests the connection to the Openstack datasource and returns the session object

        Arguments:
            source {OpenstackSource} -- the Openstack datasource to connect to

        Returns:
            Optional[connection.Connection] -- the Openstack connection object or None if the
            connection failed & a key error occured
        """
        try:
            conn_args = await self.connect_args(source)
            conn = connection.Connection(**conn_args)
            conn.authorize()
        except SDKException as e:
            return str(e), False

        return None, True

    def to_response(self, datasource: OpenstackSource) -> OpenstackResponse:
        """serializes the Openstack datasource into the key word arguments to create the response model"""
        base_args_dict = self.get_base_schema(datasource)
        options_schema = OpenstackOptions.convert(datasource)
        return OpenstackResponse(data_source=base_args_dict, options=options_schema)
