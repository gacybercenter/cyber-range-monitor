# from typing import Annotated


# from fastapi import Depends

# from openstack import connection

# from app.openstack_source.dependency import OpenstackControllerDep

# from core.errors.http_errors import HTTPBadRequest

# from .const import OPENSTACK_CONNECTION


# async def get_openstack_connection(
#     openstack_controller: OpenstackControllerDep
# ) -> connection.Connection:
#     '''dependency to get the established or new openstack connection

#     Arguments:
#         openstack_controller {OpenstackControllerDep} -- the controller dependency

#     Raises:
#         exc: HTTPBadRequest -- if the connection to openstack fails with a CONNECTION_FAILED label

#     Returns:
#         connection.Connection -- the cached or new openstack connection
#     '''
#     openstack_conn = await OPENSTACK_CONNECTION.connect(openstack_controller)
#     if not openstack_conn:
#         exc = HTTPBadRequest('Failed to connect to Guacamole')
#         exc.label = 'CONNECTION_FAILED'
#         raise exc
#     return openstack_conn

# OpenstackConnectionDep = Annotated[connection.Connection, Depends(
#     get_openstack_connection
# )]
