from typing import Annotated

import httpx
from fastapi import Depends
from openstack import connection

from range_monitor.depends import (
    APITenant,
    ContextRequired,
    CryptoServiceDep,
    DatabaseDep,
    GuacTenantRequired,
    SaltstackTenantRequired,
)
from range_monitor.sources.services.guac import GuacamoleDatasourceService
from range_monitor.sources.services.open_stack import OpenstackService
from range_monitor.sources.services.saltstack import SaltstackService

GuacTenantDep = Annotated[APITenant, Depends(GuacTenantRequired)]
SaltstackTenantDep = Annotated[APITenant, Depends(SaltstackTenantRequired)]


async def get_guacamole_service(
    db: DatabaseDep,
    crypto_service: CryptoServiceDep,
    guac_tenant: GuacTenantDep,
) -> GuacamoleDatasourceService:
    return GuacamoleDatasourceService(
        db=db,
        crypto_service=crypto_service,
        guac_tenant=guac_tenant
    )

async def get_saltstack_service(
    db: DatabaseDep,
    crypto_service: CryptoServiceDep,
    saltstack_tenant: SaltstackTenantDep,
) -> SaltstackService:

    return SaltstackService(
        db=db,
        crypto_service=crypto_service,
        salt_tenant=saltstack_tenant
    )

async def get_openstack_service(
    db: DatabaseDep,
    crypto_service: CryptoServiceDep,
    context: ContextRequired
) -> OpenstackService:
    return OpenstackService(
        db=db,
        crypto_service=crypto_service,
        openstack_tenant=context.openstack_tenant
    )

GuacamoleServiceDep = Annotated[
    GuacamoleDatasourceService,
    Depends(get_guacamole_service)
]
SaltstackServiceDep = Annotated[SaltstackService, Depends(get_saltstack_service)]
OpenstackServiceDep = Annotated[OpenstackService, Depends(get_openstack_service)]


async def current_guacamole_client(
    guac_service: GuacamoleServiceDep
) -> httpx.AsyncClient:
    return await guac_service.get_connection()

async def current_saltstack_client(
    salt_service: SaltstackServiceDep
) -> httpx.AsyncClient:
    return await salt_service.get_connection()

async def current_openstack_client(
    openstack_service: OpenstackServiceDep
) -> connection.Connection:
    return await openstack_service.get_connection()

GuacamoleClientDep = Annotated[httpx.AsyncClient, Depends(current_guacamole_client)]

SaltstackClientDep = Annotated[httpx.AsyncClient, Depends(current_saltstack_client)]

OpenstackConnectionDep = Annotated[
    connection.Connection,
    Depends(current_openstack_client)
]
