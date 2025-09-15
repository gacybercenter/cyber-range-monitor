



from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from range_monitor.guac.depends import GuacSessionServiceDep
from range_monitor.guac.schema import (
    ConnectionUrlEnvelope,
    GuacamoleConnectionList,
    KilledConnectionsResults,
)
from range_monitor.users.depends import RoleRequired, UserRoles

connections_router = APIRouter(
    dependencies=[
        Depends(RoleRequired(UserRoles.USER))
    ]
)

ActiveSince = Annotated[
    datetime | None,
    Query(
        None,
        description='Filter to connections active since this timestamp',
        example='2023-10-01T00:00:00Z',
    ),
]
OnlyProtocols = Annotated[
    list[str] | None,
    Query(
        None,
        description='Filter connections by protocol(s)',
        example=['rdp', 'vnc'],
    ),
]
ConnectionIdentifiers = Annotated[
    list[str],
    Query(
        ...,
        description='List of connection identifiers',
        example=['conn-1', 'conn-2'],
        min_length=1,
    ),
]



@connections_router.get(
    '/',
    response_model=GuacamoleConnectionList,
)
def list_connections(
    session_service: GuacSessionServiceDep,
    only_protocols: OnlyProtocols = None,
    active_since: ActiveSince = None,
) -> GuacamoleConnectionList:
    return session_service.get_connections(
        only_protocols=set(only_protocols) if only_protocols else None,
        active_since=active_since,
    )


@connections_router.get('/urls/', response_model=ConnectionUrlEnvelope)
def get_connection_urls(
    session_service: GuacSessionServiceDep,
    identifiers: ConnectionIdentifiers,
) -> ConnectionUrlEnvelope:
    '''
    Generate connectable URLs for the specified connection identifiers.

    Parameters
    ----------
    identifiers : list[str]
        List of connection identifiers to generate URLs for.

    Returns
    -------
    dict[str, str]
        Mapping of connection identifiers to their connectable URLs.

    Raises
    ------
    BadRequest
        If no connection identifiers are provided.
    '''
    return session_service.get_connection_url(identifiers)

@connections_router.delete('/kill/', response_model=KilledConnectionsResults)
def kill_connections(
    session_service: GuacSessionServiceDep,
    identifiers: ConnectionIdentifiers,
) -> KilledConnectionsResults:
    '''
    Terminate active connections for the specified connection identifiers.

    Parameters
    ----------
    identifiers : list[str]
        List of connection identifiers to terminate.

    Returns
    -------
    KilledConnectionsResults
        Results of the termination attempt, including counts of successful and ignored
        terminations.

    Raises
    ------
    BadRequest
        If no connection identifiers are provided.
    '''
    return session_service.kill_connection_identifiers(identifiers)
