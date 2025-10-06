import time

from range_monitor.guac.api import GuacamoleAPI
from range_monitor.guac.schema import (
    ConnectedUsers,
    ConnectionHistory,
    HistoryDataset,
    Topology,
    TopologyNode,
    UserConnection,
)


def _add_nested_to_stack(nested: list | dict, stack: list) -> None:
    iterable = (
        nested.values() if isinstance(nested, dict) else nested
    )
    for item in iterable:
        if isinstance(item, (list, dict)):
            stack.append(item)


def flatten_connection_tree(tree: dict) -> tuple[list[TopologyNode], int]:

    connections = []
    total_active = 0

    stack = [tree]

    while stack:
        current = stack.pop()
        if isinstance(current, list):
            _add_nested_to_stack(current, stack)
            continue

        if not isinstance(current, dict):
            continue

        if 'name' not in current or 'identifier' not in current:
            _add_nested_to_stack(current, stack)
            continue

        connection = current.copy()

        active = int(connection.get('activeConnections', 0))
        total_active += active

        if group := connection.pop('childConnectionGroups', None):
            stack.append(group)

        if conns := connection.pop('childConnections', None):
            stack.append(conns)

        connections.append(TopologyNode(
            name=connection['name'],
            identifier=connection['identifier'],
            active_connections=active,
            parent_identifier=connection.get('parentIdentifier'),
            node_type=connection.get('type'),
        ))

    return connections, total_active




class GuacamoleAPIService:

    def __init__(self, api: GuacamoleAPI) -> None:
        self.api = api

    async def get_history(self, connection_id: str) -> ConnectionHistory:

        history = await self.api.get_connection_history(connection_id)

        users = dict(map(
            lambda u: (u.username, []),
            history
        ))
        timestamps = []
        for entry in history:

            if entry.end_date:
                end = round(time.time() * 1000)
            else:
                end = entry.end_date

            elapsed = max(0, end - entry.start_date) # type: ignore
            for user, entries in users.items():
                if entry.username == user:
                    entries.append(elapsed)
                    continue
                entries.append(None)

            timestamps.append(entry.start_date)

        datasets = [
            HistoryDataset(
                label=user,
                data=entries
            ) for user, entries in users.items()
        ]

        return ConnectionHistory(
            timestamps=timestamps,
            datasets=datasets
        )

    async def get_topology(self, active_only: bool = False) -> Topology:

        connection_tree = await self.api.get_connection_group_tree()

        connections, total_active = flatten_connection_tree(connection_tree)

        if active_only:
            connections = list(filter(
                lambda c: c.is_active(),
                connections
            ))

        return Topology(
            total_active=total_active,
            nodes=connections,
            total_nodes=len(connections),
        )

    async def get_connected_users(self) -> ConnectedUsers:

        active_connections = await self.api.get_active_connections()

        active_users = [
            await self.api.get_user(conn.username)
            for conn in active_connections
        ]

        organizations: dict[str, list[UserConnection]] = {}
        for user in active_users:
            org = user.attributes.guac_organization or 'Unknown'
            organizations.setdefault(org, [])
            connection = UserConnection(
                identifier=user.identifier,
                connection_name=user.attributes.guac_full_name or 'Unknown',
                username=user.attributes.guac_email_address or 'Unknown'
            )
            organizations[org].append(connection)

        total = sum(map(len, organizations.values()))
        return ConnectedUsers(
            total=total,
            organizations=organizations
        )