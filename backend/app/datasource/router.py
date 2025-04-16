from fastapi import APIRouter

from .router_config import DatasourceRouter, create_router, Datasources

from .guacamole_source.service import GuacamoleSourceService
from .guacamole_source.schema import (
    GuacamoleRead, GuacamoleUpdate, GuacamoleCreate
)

from .openstack_source.service import OpenstackSourceService
from .openstack_source.schema import (
    OpenstackRead, OpenstackUpdate, OpenstackCreate
)


def create_datasource_router() -> APIRouter:
    '''creates the shared logic for all datasource types

    Returns:
        APIRouter -- the wrapper router for all datasource types
    '''
    openstack = DatasourceRouter(
        OpenstackSourceService,
        Datasources.openstack,
        OpenstackCreate,
        OpenstackRead,
        OpenstackUpdate
    )
    guacamole = DatasourceRouter(
        GuacamoleSourceService,
        Datasources.guacamole,
        GuacamoleCreate,
        GuacamoleRead,
        GuacamoleUpdate
    )

    routers = [openstack, guacamole]

    datasource_router = APIRouter(
        prefix='/datasources'
    )

    for router_conf in routers:
        router = create_router(router_conf)
        datasource_router.include_router(router)

    return datasource_router
