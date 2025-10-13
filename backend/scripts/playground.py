import pprint
from dataclasses import dataclass
from typing import Annotated

import guacamole
from pydantic import BaseModel, ConfigDict, Field


def to_camel_case(string: str) -> str:
    """
    Pydantic alias generator to convert snake_case to camelCase
    when `model_dump()` is called which automatically makes snake
    case to camel case conversions for keys in dicts.
    """
    words = string.split('_')
    new_name = []
    for i, word in enumerate(words):
        if i:
            new_name.append(word.capitalize())
        else:
            new_name.append(word.lower())

    return ''.join(new_name).replace('Id', 'Id')


class GuacamoleDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel_case,
        populate_by_name=True,
    )


class ActiveGuacamoleConnection(GuacamoleDTO):
    connectable: bool
    connection_identifier: str
    identifier: str
    start_date: int
    username: str
    remote_host: str


class GuacamoleConnection(GuacamoleDTO):
    identifier: str
    active_connections: int
    name: str
    parent_identifier: str | None = None
    protocol: str
    last_active: int | None = None


MaxConnections = Annotated[
    int | None,
    Field(
        alias='max-connections',
        description='The maximum number of connections that can be made to this connection',
    ),
]
MaxConnectionsPerUser = Annotated[
    int | None,
    Field(
        alias='max-connections-per-user',
        description='The maximum number of connections that can be made to this connection per user',
    ),
]


ConnectionGroupType = Annotated[
    str,
    Field(
        description=(
            'The type of connection group. One of ORGANIZATIONAL, '
            'BALANCING, or STATIC. '
            'See https://guacamole.apache.org/doc/gug/configuring-guacamole.html#connection-groups'
        ),
        alias='type',
    ),
]


class ConnectionAttributes(GuacamoleDTO):
    max_connections: MaxConnections = None
    max_connections_per_user: MaxConnectionsPerUser = None


class ConnectionGroup(GuacamoleDTO):
    active_connections: int
    attributes: ConnectionAttributes
    parent_identifier: str
    type_: ConnectionGroupType
    identifier: str
    name: str


class SubconnectionGroup(GuacamoleDTO):
    name: str
    identifier: str
    type_: ConnectionGroupType
    active_connections: int
    child_connections: list[GuacamoleConnection] = []


class ConnectionGroupConnections(GuacamoleDTO):
    name: str
    identifier: str
    type_: ConnectionGroupType
    active_connections: int
    child_connection_groups: list[SubconnectionGroup]
    child_connections: list[GuacamoleConnection]


"""
list_active_connections
list_connections
list_connection_group_connections
kill_active_connections
detail_connection
"""


def get_connection_list():
    connection_list: dict = sess.list_connections()
    pprint.pprint(connection_list)
    input()

    for conn in connection_list.values():
        connection = Connection.model_validate(conn)
        print(connection)
        print()


def get_connection_group_list():
    connection_group_list: dict = sess.list_connection_groups()  # type: ignore
    pprint.pprint(connection_group_list)
    input()

    for group in connection_group_list.values():
        print(ConnectionGroup.model_validate(group))


def get_connection_group_connections():
    connection_group_connections: dict = sess.list_connection_group_connections()  # type: ignore

    ConnectionGroupConnections.model_validate(connection_group_connections)


@dataclass(slots=True)
class GuacamoleSessionService:
    session: guacamole.session

    # list_active_connections()
    def get_active_connections(self) -> list[ActiveGuacamoleConnection]:
        active_conn_response: dict = self.session.list_active_connections()  # type: ignore
        return [
            ActiveGuacamoleConnection.model_validate(conn)
            for conn in active_conn_response.values()
        ]

    # list_connections()
    def get_all_connections(self) -> list[GuacamoleConnection]:
        all_conn_response: dict = self.session.list_connections()  # type: ignore
        return [
            GuacamoleConnection.model_validate(conn)
            for conn in all_conn_response.values()
        ]

    # list_connection_groups()
    def get_connection_group_list(self) -> list[ConnectionGroup]:
        conn_group_response: dict = self.session.list_connection_groups()  # type: ignore
        return [
            ConnectionGroup.model_validate(group)
            for group in conn_group_response.values()
        ]

    # list_connection_group_connections()
    def get_connection_group_connections(self) -> ConnectionGroupConnections:
        conn_group_response: dict = self.session.list_connection_group_connections()  # type: ignore
        return ConnectionGroupConnections.model_validate(conn_group_response)

    def get_active_connection_ids(self) -> set[int]:
        active_conn_response: dict = self.session.list_active_connections()  # type: ignore
        return {conn['identifier'] for conn in active_conn_response.values()}


def main() -> None:
    guacamole.session(
        host='https://training.gacyberrange.org/',
        username='range_provisioner',
        password='3bcd06613b24a2f729f5c947a77b2f2f',
        data_source='mysql',
    )
