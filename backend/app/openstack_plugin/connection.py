
from openstack import connection

from app.openstack_source.controller import (
    OpenstackController, OpenstackConnectionConfig
)

from extensions.datasources.connection import DatasourceConnection

from app.extensions.datasources.errors import HTTPDatasourceConnectionFailed


class OpenstackConnection(
    DatasourceConnection[OpenstackConnectionConfig, connection.Connection]
):
    async def _reconnect(self, controller: OpenstackController) -> connection.Connection:
        if not self._conn_args:
            self.clear_connection()
            raise HTTPDatasourceConnectionFailed('No connection arguments were provided.')
        return await controller.connect(self._conn_args)
        
            
    
    
        
        