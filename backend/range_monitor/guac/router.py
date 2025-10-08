from typing import Annotated

from fastapi import APIRouter, Body, Path, status

from range_monitor.guac.depends import GuacAPIDep, GuacAPIServiceDep
from range_monitor.guac.schema import (
    ConnectableEnvelope,
    ConnectedUsers,
    ConnectionHistory,
    ConnectionIdentifierBody,
    Topology,
)

guac_api_router = APIRouter()


ConnectionIdentifier = Annotated[str, Path(
    ...,
    title='Connection Identifier',
    description='The unique identifier for the connection',
)]

@guac_api_router.get('/topology', response_model=Topology)
async def get_topology(service: GuacAPIServiceDep) -> Topology:
    return await service.get_topology()

@guac_api_router.get('/connected/users/', response_model=ConnectedUsers)
async def get_connected_users(service: GuacAPIServiceDep) -> ConnectedUsers:
    return await service.get_connected_users()


@guac_api_router.get(
    '/connection/history/{connection_id}',
    response_model=ConnectionHistory
)
async def get_connection_history(
    connection_id: ConnectionIdentifier,
    service: GuacAPIServiceDep
) -> ConnectionHistory:
    return await service.get_history(connection_id)


@guac_api_router.delete(
    '/kill',
    status_code=status.HTTP_204_NO_CONTENT
)
async def kill_connections(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    api: GuacAPIDep
) -> None:
    await api.kill_connections(body.connection_identifiers)


@guac_api_router.post(
    '/connect',
    response_model=ConnectableEnvelope,
    status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
)
async def get_connectable_url(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    api: GuacAPIDep,
) -> ConnectableEnvelope:
    urls = await api.create_connectable_url(body.connection_identifiers)
    token = await api.get_token()

    return ConnectableEnvelope(
        token=token,
        url=urls
    )


'''
/connect TODO (for slideshow, slideshow_data)

'''