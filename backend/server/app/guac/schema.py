from datetime import datetime
from enum import IntEnum
from typing import Annotated, TypedDict

from pydantic import Field

from server.app.guac.client.daos import Connection, ConnectionInstance
from server.app.schema import ResponseModel

NodeToken = Annotated[
    str,
    Field(
        ..., description='The token used to authenticate the connection to the node.'
    ),
]
NodeURL = Annotated[str, Field(..., description='The URL of the node to connect to.')]
NodeName = Annotated[str, Field(..., description='The name of the node.')]
NodeID = Annotated[str, Field(..., description='The unique identifier for this node.')]
ActiveConnections = Annotated[
    int,
    Field(..., description='The number of active connections for this node.', gt=-1),
]

ParentID = Annotated[
    str, Field(description='The identifier of the parent node, if any.')
]

NodeType = Annotated[str, Field(description='The type of the node, if applicable.')]

ConnectionIdentifiers = Annotated[
    list[str],
    Field(description='A list of connection identifiers to retrieve node tokens for.'),
]


class NodeWeight(IntEnum):
    '''
    Defines the weight of a connection node in the topology.
    '''

    ROOT = 4
    GROUP = 3
    ACTIVE_CONNECTION = 2
    CONNECTION = 1


class GuacUrlScheme(ResponseModel):
    '''
    The envelope containing the information to
    produce a connectable URL for the connection
    '''

    token: NodeToken
    url: NodeURL


class HistoryDataset(TypedDict):
    '''
    A dataset within the connection history
    '''

    label: str
    data: list[int | None]


class ConnectionsHistory(ResponseModel):
    '''
    Represents historical data for a connection.
    '''

    timestamps: list[int]
    datasets: list[HistoryDataset]


class GuacNode(ResponseModel):
    '''
    A labeled connection or node in the topology.
    '''

    weight: NodeWeight
    name: NodeName
    parent_identifier: ParentID | None = None
    active_connections: ActiveConnections
    identifier: NodeID


TopologyConnections = Annotated[
    dict[str, GuacNode],
    Field(
        default_factory=dict, description='The connections mapped by their identifiers.'
    ),
]
TopologyGroups = Annotated[
    dict[str, GuacNode],
    Field(description='The connection groups in the topology mapped by identifier.'),
]

InstancesList = Annotated[
    list[ConnectionInstance], Field(description='A list of connection instances.')
]


class TopologyModel(ResponseModel):
    '''
    Represents the hierarchical structure of connections and
    connection groups.
    '''

    total_labels: int = 0
    total_active: int = 0
    root: GuacNode
    connections: TopologyConnections = Field(default_factory=dict)
    groups: TopologyGroups = Field(default_factory=dict)


class UserConnection(ResponseModel):
    '''
    Represents an active connection associated with a user.
    '''

    identifier: NodeID
    connection_name: NodeName
    username: str
    last_active: datetime


class ActiveOrganization(ResponseModel):
    '''
    Represents an organization with active connections.
    '''

    name: NodeName
    total: ActiveConnections = 0
    connections: dict[str, UserConnection] = Field(
        default_factory=dict,
        description='A mapping of connection identifiers to user connections.',
    )


class ConnectionActivity(ResponseModel):
    '''
    An overview of the activity inside of the connected
    Guacamole adapter.
    '''

    total_active: ActiveConnections
    organizations: dict[str, ActiveOrganization]
    instances: InstancesList


FetchedAt = Annotated[
    datetime, Field(..., description='The timestamp when the data was fetched.')
]


class ConnectionTimeline(ResponseModel):
    '''for `connection graph`'''

    fetched_at: FetchedAt
    users: list[UserConnection] = Field(
        default_factory=list, description='A list of active user connections.'
    )
    total: int


class ConnectedOrganization(ResponseModel):
    name: str
    role: str | None = None


class GuacamoleSummary(ResponseModel):
    hostname: str = Field(
        ..., description='The hostname of the connected Guacamole instance.'
    )
    username: str = Field(..., description='The username of the connected user.')
    last_active: datetime
    active_connections: int
    organization: ConnectedOrganization


class ConnectionIdentifierBody(ResponseModel):
    '''
    Request body containing connection identifiers
    '''

    connection_identifiers: ConnectionIdentifiers


class ConnectionSessions(ResponseModel):
    '''
    Represents a connection, and its active instances.
    '''

    connection: Connection
    instances: list[ConnectionInstance] = Field(
        default_factory=list,
        description='A list of active connection instances for this connection.',
    )


class LiveConnections(ResponseModel):
    '''
    Represents live connections and their active sessions.
    '''

    total_active: ActiveConnections
    sessions: dict[str, ConnectionSessions] = Field(
        default_factory=dict,
        description='A mapping of connection identifiers to connection details.',
    )
