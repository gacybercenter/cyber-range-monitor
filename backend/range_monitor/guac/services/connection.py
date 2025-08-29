# import time

# from extensions.datasources.connection import DatasourceConnection
# from app.extensions.datasources.errors import HTTPDatasourceConnectionFailed

# from app.guacamole_source.controller import GuacamoleController, GuacamoleSessionConfig


# class GuacamoleConnection(DatasourceConnection[GuacamoleSessionConfig, guacamole.session]):
#     async def _reconnect(self, controller: GuacamoleController) -> guacamole.session:
#         if not self._conn_args:
#             self.clear_connection()
#             raise HTTPDatasourceConnectionFailed(
#                 'No connection arguments were provided'
#             )
#         self._conn = await controller.connect(self._conn_args)
#         if not self._conn:
#             self.clear_connection()
#             raise HTTPDatasourceConnectionFailed(
#                 'Connection failed likely due to invalid credentials or a misconfiguration'
#             )

#         self.last_connected = time.time()
#         return self._conn
