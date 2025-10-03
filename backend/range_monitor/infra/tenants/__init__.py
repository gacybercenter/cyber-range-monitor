'''
The datasource tenants that are managed by the application.
'''

from range_monitor.infra.tenants._api_clients import (
    APITenant,
    HttpTenantConfig,
    HttpTenantPool,
    TenantContext,
)
from range_monitor.infra.tenants._auth import AuthScheme, InvalidAPICredentials
from range_monitor.infra.tenants._openstack import (
    ConnectionCredentials,
    InvalidOpenstackCredentials,
    OpenstackTenant,
    close_openstack_connection,
    create_openstack_connection,
)
from range_monitor.infra.tenants.config import HttpxConfig

__all__ = [
    'AuthScheme',
    'HttpxConfig',
    'HttpTenantPool',
    'APITenant',
    'TenantContext',
    'InvalidAPICredentials',
    'ConnectionCredentials',
    'OpenstackTenant',
    'InvalidOpenstackCredentials',
    'create_openstack_connection',
    'close_openstack_connection',
    'HttpTenantConfig',
]
