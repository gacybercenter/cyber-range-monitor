# import time
# from typing import Generic, TypeVar

# from app.extensions.security import crypto

# from app.extensions.datasources.controller import DatasourceController


# from .schema import DatasourceConnectionModel

# from .const import CONNECTION_TIMEOUT


# ConnSchema = TypeVar('ConnSchema', bound=DatasourceConnectionModel)

# # the type of the connection object (e.g guacamole.session)
# ConnT = TypeVar('ConnT')


# class DatasourceConnection(Generic[ConnSchema, ConnT]):
#     def __init__(self) -> None:
#         self._conn: ConnT | None = None
#         self._conn_args: ConnSchema | None = None
#         self.last_connected: float = 0

#     async def _reconnect(self, controller: DatasourceController) -> ConnT:
#         raise NotImplementedError

#     def connection_expired(self) -> bool:
#         return time.time() - self.last_connected > CONNECTION_TIMEOUT

#     async def connect(self, controller: DatasourceController) -> ConnT | None:
#         '''Connects a datasource to an object representation of the datasource
#         (e.g a Guacamole session object) and returns the connected object.

#         The connection will persist for 5 minutes before it expires and needs to be reconnected
#         unless the enabled datasource has changed or the connection arguments have changed.

#         Arguments:
#             controller {DatasourceController} -- the datasource controller

#         Returns:
#             ConnT | None -- the connected datasource or None if failed
#         '''

#         enabled_source = await controller.get_enabled_source()
#         if not enabled_source:
#             return None

#         connect_args: ConnSchema = await controller.connect_args(enabled_source)
#         if not self._conn or not self._conn_args:
#             self._conn_args = connect_args
#             return await self._reconnect(controller)

#         if self.connection_expired():
#             return await self._reconnect(controller)

#         cur_args = self._conn_args.serialize()
#         new_args = connect_args.serialize()
#         if not crypto.compare_dict_hashes(cur_args, new_args):
#             self._conn_args = connect_args
#             return await self._reconnect(controller)

#         return self._conn

#     def clear_connection(self) -> None:
#         '''Clears the connection object and connection arguments and should be done 
#         upon an error occurring during the connection process
#         '''
#         self._conn = None
#         self._conn_args = None
#         self.last_connected = 0
