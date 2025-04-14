from fastapi import APIRouter

from .router_config import DatasourceRouter, Datasources

from .guacamole_source.service import GuacamoleSourceService
from .guacamole_source.schema import GuacamoleRead, GuacamoleUpdate

from .openstack_source.controller import OpenstackSourceService
from .openstack_source.schema import OpenstackRead, OpenstackUpdate


class GuacamoleRouter(DatasourceRouter[GuacamoleRead, GuacamoleUpdate]):
    '''The router for the Guacamole datasource'''

    def __init__(self) -> None:
        super().__init__(
            GuacamoleSourceService,
            Datasources.guacamole
        )


class OpenstackRouter(DatasourceRouter[OpenstackRead, OpenstackUpdate]):
    '''The router for the Openstack datasource'''

    def __init__(self) -> None:
        super().__init__(
            OpenstackSourceService,
            Datasources.openstack
        )


def create_datasource_router() -> APIRouter:
    '''creates the shared logic for all datasource types
    
    Returns:
        APIRouter -- the wrapper router for all datasource types
    '''
    routers: list[DatasourceRouter] = [
        GuacamoleRouter(),
        OpenstackRouter()
    ]

    datasource_router = APIRouter(
        prefix='/datasources'
    )

    for router_conf in routers:
        router = router_conf.register_routes()
        datasource_router.include_router(router)

    return datasource_router
