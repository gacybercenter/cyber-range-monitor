from server.app.data_sources.routers.guac import guac_router
from server.app.data_sources.routers.open_stack import openstack_router
from server.app.data_sources.routers.salt_stack import saltstack_router

__all__ = [
    'guac_router',
    'openstack_router',
    'saltstack_router',
]
