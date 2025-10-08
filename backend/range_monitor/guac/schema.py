
from datetime import datetime
from enum import IntEnum
from typing import Annotated

from pydantic import Field

from range_monitor.guac.api.dtos import Connection, ConnectionInstance
from range_monitor.schema.http import ResponseModel

NodeToken = Annotated[
    str,
    Field(
        ...,
        description='The token used to authenticate the connection to the node.'
    )
]
NodeURL = Annotated[
    str,
    Field(
        ...,
        description='The URL of the node to connect to.'
    )
]


NodeName = Annotated[
    str,
    Field(
        ...,
        description='The name of the node.'
    )
]
NodeID = Annotated[
    str,
    Field(
        ...,
        description='The unique identifier for this node.'
    )
]
ActiveConnections = Annotated[
    int,
    Field(
        ...,
        description='The number of active connections for this node.',
        gt=-1
    )
]

ParentID = Annotated[
    str,
    Field(
        description='The identifier of the parent node, if any.'
    )
]

NodeType = Annotated[
    str,
    Field(description='The type of the node, if applicable.')
]


class ConnectionWeight(IntEnum):
    ROOT = 4
    GROUP = 3
    ACTIVE_CONNECTION = 2
    CONNECTION = 1

class ConnectableEnvelope(ResponseModel):
    token: NodeToken
    url: NodeURL

class HistoryDataset(ResponseModel):
    label: str
    data: list[int | None]

class ConnectionHistory(ResponseModel):
    timestamps: list[int]
    datasets: list[HistoryDataset]


class ConnectionLabel(ResponseModel):
    weight: ConnectionWeight
    name: NodeName
    parent_identifier: ParentID | None = None
    active_connections: ActiveConnections
    identifier: NodeID


class TopologyModel(ResponseModel):
    total_labels: int = 0
    total_active: int = 0
    root: ConnectionLabel
    connections: dict[str, ConnectionLabel] = Field(
        default_factory=dict,
        description='A mapping of node identifiers to connection labels.'
    )
    groups: dict[str, ConnectionLabel] = Field(
        default_factory=dict,
        description='A mapping of group identifiers to connection labels.'
    )


class UserConnection(ResponseModel):
    identifier: NodeID
    connection_name: NodeName
    username: str

class ConnectedOrganization(ResponseModel):
    name: NodeName = Field(..., description='The name of the organization.')
    total: int = Field(
        default=0,
        description='The total number of active connections for this organization.'
    )
    connections: dict[str, UserConnection] = Field(
        default_factory=dict,
        description='A mapping of connection identifiers to user connections.'
    )

class ConnectionSummary(ResponseModel):
    total_active: int
    organizations: dict[str, ConnectedOrganization]




FetchedAt = Annotated[
    datetime,
    Field(
        ...,
        description='The timestamp when the data was fetched.'
    )
]
class ConnectionTimeline(ResponseModel):
    '''for `connection graph`'''
    fetched_at: FetchedAt
    users: list[UserConnection]
    total: int

ConnectionIdentifiers = Annotated[
    list[str],
    Field(
        description='A list of connection identifiers to retrieve node tokens for.'
    )
]

class ConnectionIdentifierBody(ResponseModel):
    connection_identifiers: ConnectionIdentifiers


class ConnectionSessions(ResponseModel):
    connection: Connection
    instances: list[ConnectionInstance] = Field(
        default_factory=list,
        description='A list of active connection instances for this connection.'
    )


class LiveConnections(ResponseModel):

    total_connections: int = Field(
        default=0,
        description='The total number of connections.'
    )
    sessions: dict[str, ConnectionSessions] = Field(
        default_factory=dict,
        description='A mapping of connection identifiers to connection details.'
    )