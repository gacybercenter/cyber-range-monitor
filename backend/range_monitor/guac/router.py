from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.responses import StreamingResponse

from range_monitor.auth.depends import AdminRequired
from range_monitor.guac.depends import GuacRestServiceDep
from range_monitor.guac.schema import (
    ConnectionActivity,
    ConnectionIdentifierBody,
    ConnectionsHistory,
    ConnectionTimeline,
    GuacamoleSummary,
    GuacUrlScheme,
    TopologyModel,
)

guac_api_router = APIRouter(dependencies=[Depends(AdminRequired)])


ConnectionIdentifier = Annotated[
    str,
    Path(
        ...,
        title='Connection Identifier',
        description='The unique identifier for the connection',
    ),
]

ActiveOnly = Annotated[
    bool,
    Query(
        title='Active Only',
        description='If true, only connections with active instances will be included.',
    ),
]

HistorySince = Annotated[
    datetime,
    Query(
        title='History Since',
        description='If provided, only history entries after this timestamp.',
    ),
]

GroupIdentifier = Annotated[
    str,
    Path(
        ...,
        title='Connection Group Identifier',
        description='The unique identifier for the connection group',
    ),
]


@guac_api_router.get('/', response_model=GuacamoleSummary)
async def get_guacamole_summary(service: GuacRestServiceDep) -> GuacamoleSummary:
    """
    Provides a summary of the Guacamole data source including
    details about the connected datasource
    """
    return await service.get_summary()


@guac_api_router.get('/topology', response_model=TopologyModel)
async def get_topology(service: GuacRestServiceDep) -> TopologyModel:
    """
    Returns the full topology of connections from the root.
    """
    return await service.topology.fetch()


@guac_api_router.get('/topology/{group_id}/', response_model=TopologyModel)
async def get_subtopology(
    group_id: GroupIdentifier, service: GuacRestServiceDep
) -> TopologyModel:
    """
    Gets the topology of the a connection group
    """
    return await service.topology.fetch(group_id)


@guac_api_router.get('/timeline/', response_model=ConnectionTimeline)
async def get_timeline(service: GuacRestServiceDep) -> ConnectionTimeline:
    """
    Returns the timestamped history of connection events.
    """
    return await service.history.get_connections_timeline()


@guac_api_router.get('/history/{connection_id}', response_model=ConnectionsHistory)
async def get_connection_history(
    connection_id: ConnectionIdentifier, service: GuacRestServiceDep
) -> ConnectionsHistory:
    """
    Retrieves the connection history for a specific connection.
    """
    return await service.history.get_connections_history(connection_id)


@guac_api_router.delete(
    '/kill/',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def kill_connections(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    api: GuacRestServiceDep,
) -> None:
    """
    Kills one or more active connections by their identifiers.
    """
    await api.kill_identifiers(body.connection_identifiers)


@guac_api_router.post(
    '/connect/',
    response_model=GuacUrlScheme,
    status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
)
async def get_connectable_url(
    body: Annotated[ConnectionIdentifierBody, Body(...)],
    guac_service: GuacRestServiceDep,
) -> GuacUrlScheme:
    """
    Gets a Guacamole URL that can be used to connect to one or more
    connections or active instances.
    """
    return await guac_service.get_connection_url(body.connection_identifiers)


@guac_api_router.get(
    '/connections/activity/',
    response_model=ConnectionActivity,
)
async def get_connection_overview(service: GuacRestServiceDep) -> ConnectionActivity:
    return await service.get_connection_activity()


@guac_api_router.get('/history/connections/', response_class=StreamingResponse)
async def stream_connections_history(
    service: GuacRestServiceDep,
    active_only: ActiveOnly = False,
    since: HistorySince | None = None,
) -> StreamingResponse:
    """
    Streams the connection history for all connections as NDJSON.
    """
    return await service.history.stream_history(
        'connections', active_only=active_only, since=since
    )


@guac_api_router.get('/history/users/', response_class=StreamingResponse)
async def stream_users_history(
    service: GuacRestServiceDep,
    active_only: ActiveOnly = False,
    since: HistorySince | None = None,
) -> StreamingResponse:
    """
    Streams the user history for all users as NDJSON.
    """
    return await service.history.stream_history(
        'users', active_only=active_only, since=since
    )
