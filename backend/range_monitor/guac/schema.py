
from typing import Annotated

from pydantic import Field

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


class ConnectableEnvelope(ResponseModel):
    token: NodeToken
    url: NodeURL

class HistoryDataset(ResponseModel):
    label: str
    data: list[int | None]

class ConnectionHistory(ResponseModel):
    timestamps: list[int]
    datasets: list[HistoryDataset]





class TopologyNode(ResponseModel):
    name: str = Field(
        ...,
        description='The name of the node.'
    )
    identifier: str = Field(
        ...,
        description='The unique identifier for this node.'
    )
    active_connections: int = Field(
        0,
        description='The number of active connections for this node.'
    )
    parent_identifier: str | None = Field(
        None,
        description='The identifier of the parent node, if any.'
    )
    node_type: str | None = Field(
        None,
        description='The type of the node, if applicable.'
    )

    def is_active(self) -> bool:
        return self.active_connections > 0

class Topology(ResponseModel):
    total_active: int
    total_nodes: int
    nodes: list[TopologyNode]


class UserConnection(ResponseModel):
    identifier: str
    connection_name: str
    username: str

class ConnectedUsers(ResponseModel):
    total: int
    organizations: dict[str, list[UserConnection]]



class ConnectionIdentifierBody(ResponseModel):
    connection_identifiers: list[str] = Field(
        ...,
        description='A list of connection identifiers to retrieve node tokens for.'
    )