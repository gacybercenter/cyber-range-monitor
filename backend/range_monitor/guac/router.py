from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status

from range_monitor.auth.depends import AdminRequired
from range_monitor.guac.depends import GuacAPIServiceDep
from range_monitor.guac.schema import (
    ConnectableEnvelope,
    ConnectionHistory,
    ConnectionIdentifierBody,
    ConnectionOverview,
    ConnectionSessions,
    ConnectionTimeline,
    GuacamoleSummary,
    LiveConnections,
    TopologyModel,
)

guac_api_router = APIRouter(
    dependencies=[Depends(AdminRequired)]
)


ConnectionIdentifier = Annotated[str, Path(
    ...,
    title='Connection Identifier',
    description='The unique identifier for the connection',
)]

@guac_api_router.get(
    '/',
    response_model=GuacamoleSummary
)
async def get_guacamole_summary(service: GuacAPIServiceDep) -> GuacamoleSummary:
    '''
    Provides a summary of the Guacamole data source including
    details about the connected datasource
    '''
    return await service.datasource_summary()


@guac_api_router.get('/topology', response_model=TopologyModel)
async def get_topology(service: GuacAPIServiceDep) -> TopologyModel:
    '''
    Returns the full topology of connections from the root.
    '''
    return await service.get_topology()

@guac_api_router.get(
    '/topology/{group_id}/',
    response_model=TopologyModel
)
async def get_group_topology(
    group_id: Annotated[str, Path(
        ...,
        title='Connection Group Identifier',
        description='The unique identifier for the connection group',
    )],
    service: GuacAPIServiceDep
) -> TopologyModel:
    '''
    Gets the topology of the a connection group
    '''
    if group_id == 'ROOT':
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail='Use /topology/ endpoint for root group.',
            headers={
                'Location': '/guacamole/topology/'
            }
        )

    return await service.get_group_topology(group_id)

@guac_api_router.get(
    '/connections/timeline',
    response_model=ConnectionTimeline
)
async def get_connected_users(service: GuacAPIServiceDep) -> ConnectionTimeline:
    '''
    Returns the timestamped history of connection events.
    '''
    return await service.get_timeline()


@guac_api_router.get(
    '/connection/history/{connection_id}',
    response_model=ConnectionHistory
)
async def get_connection_history(
    connection_id: ConnectionIdentifier,
    service: GuacAPIServiceDep
) -> ConnectionHistory:
    '''
    Retrieves the connection history for a specific connection.
    '''
    return await service.get_history(connection_id)


@guac_api_router.delete(
    '/kill/',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def kill_connections(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    api: GuacAPIServiceDep,
) -> None:
    await api.kill_connections(body.connection_identifiers)


@guac_api_router.post(
    '/connect/url',
    response_model=ConnectableEnvelope,
    status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
)
async def get_connectable_url(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    guac_service: GuacAPIServiceDep,
) -> ConnectableEnvelope:
    url = await guac_service.get_connectable_url(body.connection_identifiers)

    return ConnectableEnvelope(
        token=guac_service.api_spec.client_token,
        url=url
    )

@guac_api_router.get(
    '/connections/instances/',
    response_model=LiveConnections
)
async def get_live_connections(
    service: GuacAPIServiceDep
) -> LiveConnections:
    return await service.get_live_connections()


@guac_api_router.get(
    '/connection/{connect_id}/instances',
    response_model=ConnectionSessions,
)
async def get_connection_sessions(
    connect_id: ConnectionIdentifier,
    service: GuacAPIServiceDep
) -> ConnectionSessions:
    return await service.get_connection_sessions(connect_id)


@guac_api_router.get(
    '/connections/overview/',
    response_model=ConnectionOverview,
)
async def get_connection_overview(
    service: GuacAPIServiceDep
) -> ConnectionOverview:
    return await service.get_connection_overview()
