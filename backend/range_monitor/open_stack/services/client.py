from typing import Final

from openstack import connection
from openstack import exceptions as openstack_error

from range_monitor.datasource.connection_abc import (
    ConnectionResult,
    DatasourceConnection,
    DatasourceConnectionError,
)
from range_monitor.datasource.model import OpenStack


class _OpenstackConnection(DatasourceConnection[connection.Connection, OpenStack]):
    """
    Manages a connection to an OpenStack datasource.
    """

    @classmethod
    def create_client(
        cls, datasource: OpenStack, password: str
    ) -> ConnectionResult[connection.Connection]:

        auth = {
            'auth_url': datasource.auth_url,
            'username': datasource.username,
            'password': password,
            'user_domain_name': datasource.user_domain_name,
        }
        # if you include a null arg, otherwise valid arguments
        # cause a 401, funtimes 
        if datasource.project_id:
            auth['project_id'] = datasource.project_id

        if datasource.project_name:
            auth['project_name'] = datasource.project_name

        if datasource.project_domain_name:
            auth['project_domain_name'] = datasource.project_domain_name

        conn = connection.Connection(
            region_name=datasource.region_name,
            auth=auth,
            identity_api_version=datasource.identity_api_version,
        )

        try:
            conn.authorize()
        except openstack_error.SDKException as e:
            return ConnectionResult(client=None, error=str(e))

        return ConnectionResult(client=conn, error=None)

    async def refresh_auth(self) -> None:
        try:
            self.client.authorize()
        except openstack_error.SDKException:
            await self.disconnect()
            raise DatasourceConnectionError(
                'openstack',
                'Failed to refresh connection, datasource credentials may be stale'
            )




openstack_client: Final[_OpenstackConnection] = _OpenstackConnection()