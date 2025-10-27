from typing import Annotated

import httpx
from fastapi import Depends
from openstack import connection

from server.app.data_sources.services.guac import GuacamoleDatasourceService
from server.app.data_sources.services.open_stack import OpenstackService
from server.app.data_sources.services.saltstack import SaltstackService
from server.app.depends import (
    DatabaseDep,
    GuacRequired,
    OpenstackRequired,
    SaltstackRequired,
)
from server.external.adapters import ApiClient

GuacTenantDep = Annotated[ApiClient, Depends(GuacRequired)]  # type: ignore
SaltstackTenantDep = Annotated[ApiClient, Depends(SaltstackRequired)]  # type: ignore


async def get_guacamole_service(  # noqa: RUF029
    db: DatabaseDep,
    guac_tenant: GuacTenantDep,
) -> GuacamoleDatasourceService:
    return GuacamoleDatasourceService(
        db=db,
        guac_tenant=guac_tenant
    )


async def get_saltstack_service(  # noqa: RUF029
    db: DatabaseDep,
    saltstack_tenant: SaltstackTenantDep,
) -> SaltstackService:
    return SaltstackService(
        db=db,
        salt_tenant=saltstack_tenant
    )


async def get_openstack_service(  # noqa: RUF029
    db: DatabaseDep,
    openstack: OpenstackRequired,
) -> OpenstackService:
    return OpenstackService(
        db=db,
        openstack_tenant=openstack
    )


GuacamoleServiceDep = Annotated[
    GuacamoleDatasourceService, Depends(get_guacamole_service)
]
SaltstackServiceDep = Annotated[SaltstackService, Depends(get_saltstack_service)]
OpenstackServiceDep = Annotated[OpenstackService, Depends(get_openstack_service)]


async def current_guacamole_client(
    guac_service: GuacamoleServiceDep,
) -> httpx.AsyncClient:
    return await guac_service.get_connection()


async def current_saltstack_client(
    salt_service: SaltstackServiceDep,
) -> httpx.AsyncClient:
    return await salt_service.get_connection()


async def current_openstack_client(
    openstack_service: OpenstackServiceDep,
) -> connection.Connection:
    return await openstack_service.get_connection()


GuacamoleClientDep = Annotated[httpx.AsyncClient, Depends(current_guacamole_client)]

SaltstackClientDep = Annotated[httpx.AsyncClient, Depends(current_saltstack_client)]

OpenstackConnectionDep = Annotated[
    connection.Connection, Depends(current_openstack_client)
]
