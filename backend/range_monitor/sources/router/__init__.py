from range_monitor.sources.router.guac import guac_router
from range_monitor.sources.router.open_stack import openstack_router
from range_monitor.sources.router.salt_stack import saltstack_router

__all__ = [
    'openstack_router',
    'saltstack_router',
    'guac_router',
]
