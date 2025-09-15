from typing import Annotated

from pydantic import Field

from range_monitor.guac.dtos import (
    ActiveConnectionProfile,
    ActiveGuacamoleConnection,
    Connection,
    ConnectionGroup,
    ConnectionInstance,
    ConnectionInstanceInfo,
)
from range_monitor.schema import ResponseModel

ActiveConnectionList = Annotated[
    list[ConnectionInstanceInfo],
    Field(
        description='List of active connections',
    ),
]

ActiveUsernameList = Annotated[
    list[str],
    Field(
        description='List of unique usernames with active connections',
    ),
]

TotalActive = Annotated[
    int,
    Field(
        description='Total number of active connections',
    ),
]

ConnectableUrl = Annotated[
    str,
    Field(
        description='A connectable URL for the specified connection',
    ),
]

ConnectionGroupMapping = Annotated[
    dict[str, ConnectionGroup],
    Field(
        description='Mapping of connection group names to their details',
    ),
]

ActiveProfileMapping = Annotated[
    dict[str, ActiveConnectionProfile],
    Field(
        description='Mapping of connection identifiers to their active connection profiles',
    ),
]




class GuacamoleActiveInstances(ResponseModel):
    connected_usernames: list[str] = Field(
        default_factory=list,
        description='List of unique usernames with active connections to this connection',
    )
    instances: dict[str, ConnectionInstanceInfo] = Field(
        default_factory=dict,
        description='Mapping of organizations to their active connection instances',
    )
    profiles: list[ActiveConnectionProfile] = Field(
        default_factory=list,
        description='List of active connection profiles for this connection',
    )

class GuacamoleConnectionList(ResponseModel):
    connections: list[Connection] = Field(
        default_factory=list,
        description='List of all connections in the Guacamole system',
    )
    total: int = Field(
        default=0, description='Total number of connections in the system'
    )
    active_connections: dict[str, list[ConnectionInstance]] = Field(
        default_factory=dict,
        description='Mapping of connection identifiers to their active connection instances',
    )


class ActiveInstancesList(ResponseModel):
    connections: ActiveConnectionList
    active_usernames: ActiveUsernameList
    total_active: TotalActive


class ConnectionUrlEnvelope(ResponseModel):
    connectable_url: ConnectableUrl
    active_connections: dict[str, list[ActiveGuacamoleConnection]] = Field(
        ...,
        description='Mapping of connection identifiers to their existing active connections',
    )


class ConnectionGroupInfo(ResponseModel):
    total_active_connections: TotalActive
    active_connection_groups: ConnectionGroupMapping
    inactive_connection_groups: ConnectionGroupMapping


class ConnectionProfiles(ResponseModel):
    profiles: ActiveProfileMapping
    active_usernames: ActiveUsernameList
    total_active: TotalActive



class KilledConnectionIdentifiers(ResponseModel):
    killed: list[str] = Field(
        default_factory=list,
        description='List of connection identifiers that were killed',
    )
    ignored: list[str] = Field(
        default_factory=list,
        description='List of connection identifiers for the connections that were ignored',
    )


class KilledConnectionsResults(ResponseModel):
    total_killed: int = Field(
        default=0, description='Total number of connections that were killed'
    )
    connections: KilledConnectionIdentifiers = Field(
        default_factory=KilledConnectionIdentifiers,
        description='Details of killed and ignored connection identifiers',
    )
    succes: bool = Field(
        default=True, description='Indicates if the kill operation was successful'
    )
    guacamole_response: dict = Field(
        default_factory=dict,
        description='Raw response from the Guacamole server after attempting to kill connections',
    )

    def add_ignored(self, identifier: str) -> None:
        self.connections.ignored.append(identifier)

    def extend_kill_list(self, connection_ids: list[str]) -> None:
        self.connections.killed.extend(connection_ids)
        self.total_killed += len(connection_ids)


