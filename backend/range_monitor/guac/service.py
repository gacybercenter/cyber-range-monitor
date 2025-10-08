import asyncio
import base64
import time
from datetime import UTC, datetime
from typing import Literal

import httpx

from range_monitor.errors import ResourceNotFound
from range_monitor.guac import topology as guac_topology
from range_monitor.guac.api import guac_client
from range_monitor.guac.api.dtos import (
    Connection,
    ConnectionInstance,
    GuacUser,
    HistoryEntry,
)
from range_monitor.guac.schema import (
    ConnectedOrganization,
    ConnectionHistory,
    ConnectionOverview,
    ConnectionSessions,
    ConnectionTimeline,
    GuacamoleSummary,
    HistoryDataset,
    LiveConnections,
    TopologyModel,
    UserConnection,
)


def _map_active_connections(
    key_value_pair: tuple[str, dict]
) -> tuple[str, ConnectionInstance]:
    key, value = key_value_pair

    return key, ConnectionInstance.convert(value)

def _map_connections(key_value_pair: tuple[str, dict]) -> tuple[str, Connection]:
    key, value = key_value_pair

    return key, Connection.convert(value)

'''TODO

- Implement streaming for api operation (see guac_client.py) for
`list_users_history` and `list_connections_history`, StreamingResponse
that yields the items for the frontend to consume individually, response
size for the individual requests is MASSIVE (40k+ entries)

- Individual routes for fetching details about the individual connections
and routes to fetch as needed for the frontend

- Caching strategy for topology, fetch one, if diff, only include edited, accept
some query param or header to check a cache of a hash for each, leverage msgspec
and redis


'''

def parse_last_active(last_active: int | None) -> datetime:
    if last_active is not None:
        last_active_int = int(last_active)
        if last_active_int > 1e10:
            last_active_int = last_active_int // 1000
    else:
        last_active_int = time.time()

    try:
        return datetime.fromtimestamp(last_active_int, tz=UTC)
    except Exception:
        return datetime.now(UTC)

class GuacamoleAPIService:
    '''
    notes:

    - If more methods are needed, consider creating sub services or other modules (>500 lines)
    - `guac_client` is a thin api wrapper, it should NOT parse the response content since
    schema validation / generation is expensive and a 'as needed' approach is better

    - the `map()` is just a builtin C implementation of a list comprehension, it is
    better for large datasets since its done in C

    - if your the next guy working on this, and the todo items are still here, sorry
    and best of luck.
    '''
    def __init__(self, client: httpx.AsyncClient, data_source: str) -> None:
        self.api_spec = guac_client.create_client_spec(
            client=client,
            data_source=data_source
        )

    async def get_topology(self) -> TopologyModel:
        '''
        Gets and builds the full topology from Guacamole

        Returns
        -------
        TopologyModel
            The complete, organized topology with labels
            and weights for connections and groups.
        '''
        root_json = await guac_client.get_connection_group(self.api_spec, 'ROOT')

        root_label = guac_topology.create_root_label(
            data=root_json,
            hostname=str(self.api_spec.client.base_url)
        )

        topology = TopologyModel(
            root=root_label
        )
        groups, connections = await asyncio.gather(*(
            guac_client.list_connection_groups(self.api_spec),
            guac_client.list_connections(self.api_spec)
        ))

        guac_topology.build_labels(
            topology,
            connection_groups=groups,
            connections=connections
        )

        return topology

    async def get_group_topology(self, group_id: str) -> TopologyModel:
        '''
        Builds a topology model for a specific connection group and collects
        the associated child connections and groups.

        Parameters
        ----------
        group_id : str
            The identifier for the connection group to build the topology for.

        Returns
        -------
        TopologyModel

        Raises
        ------
        ResourceNotFound
            If the specified connection group does not exist.
        '''
        groups, connections = await asyncio.gather(*(
            guac_client.list_connection_groups(self.api_spec),
            guac_client.list_connections(self.api_spec)
        ))

        topology = guac_topology.create_group_topology(
            group_id,
            group_data=groups,
            connections=connections
        )
        if topology is None:
            raise ResourceNotFound(f'guacamole_connection_group:{group_id}')

        return topology


    async def get_history(self, connection_id: str) -> ConnectionHistory:
        '''
        Retrieves the connection history for a specific connection

        Parameters
        ----------
        connection_id : str

        Returns
        -------
        ConnectionHistory
        '''

        response = await guac_client.get_connection_history(
            self.api_spec,
            connection_id
        )

        history: list[HistoryEntry] = []
        users: dict[str, list[int | None]] = {}
        for json_entry in response:
            history_entry = HistoryEntry.convert(json_entry)
            history.append(history_entry)
            users.setdefault(history_entry.username, [])


        start_dates = []
        for entry in history:
            elapsed = entry.calc_elapsed()
            start_dates.append(entry.start_date)

            for user, entries in users.items():
                if entry.username == user:
                    entries.append(elapsed)

                entries.append(None)


        datasets = [
            HistoryDataset(
                label=user,
                data=entries
            ) for user, entries in users.items()
        ]

        return ConnectionHistory(
            timestamps=sorted(start_dates),
            datasets=datasets
        )

    async def datasource_summary(self) -> GuacamoleSummary:
        response = await guac_client.get_self(self.api_spec)
        attributes: dict = response.get('attributes', {})
        hostname = str(self.api_spec.client.base_url)

        last_active = response.get('lastActive', None)
        if last_active is not None:
            last_active_int = int(last_active)
            if last_active_int > 1e10:
                last_active_int = last_active_int // 1000
        else:
            last_active_int = time.time()

        try:
            last_active_dt = datetime.fromtimestamp(last_active_int, tz=UTC)
        except Exception:
            last_active_dt = datetime.now(UTC)

        active_connections = await guac_client.list_active_connections(self.api_spec)

        return GuacamoleSummary(
            username=response['username'],
            last_active=last_active_dt,
            hostname=hostname,
            organization_role=attributes.get('guac-organization-role', 'Unknown'),
            organization=attributes.get('guac-organization', 'Unknown'),
            active_connections=len(active_connections),
        )


    async def get_connection_overview(self) -> ConnectionOverview:
        '''
        Summarizes the current active connections by organization

        Returns
        -------
        ConnectionOverview
        '''

        response = await guac_client.list_active_connections(self.api_spec)

        active_connections: dict[str, ConnectionInstance] = {}

        for instance_json in response.values():
            instance = ConnectionInstance.convert(instance_json)
            active_connections[instance.identifier] = instance

        active_users = await asyncio.gather(*(
            guac_client.get_user(self.api_spec, conn.username)
            for conn in active_connections.values()
        ))

        organizations: dict[str, ConnectedOrganization] = {}
        running_total = 0
        for user_response in active_users:
            user = GuacUser.convert(user_response)
            org_name = user.attributes.guac_organization or 'Unknown'

            if not (org := organizations.get(org_name)):
                org = ConnectedOrganization(
                    name=org_name
                )
                organizations[org_name] = org

            org.total += 1
            running_total += 1
            org.connections[user.username] = UserConnection(
                identifier=user.username,
                connection_name=user.attributes.guac_full_name or 'Unknown',
                username=user.attributes.guac_email_address or 'Unknown',
                last_active=parse_last_active(user.last_active),
            )

        return ConnectionOverview(
            total_active=running_total,
            organizations=organizations,
            instances=list(active_connections.values())
        )


    async def get_timeline(self) -> ConnectionTimeline:
        '''
        Retrieves a timeline of currently active connections

        Returns
        -------
        ConnectionTimeline
        '''


        active_conn, all_conns = await asyncio.gather(*(
            guac_client.list_active_connections(self.api_spec),
            guac_client.list_connections(self.api_spec)
        ))

        active_connections = list(map(
            ConnectionInstance.convert,
            active_conn.values()
        ))
        connections_map = dict(map(
            _map_connections,
            all_conns.items()
        ))

        def _map_connection(conn: ConnectionInstance) -> UserConnection:
            connection = connections_map[conn.connection_identifier]
            return UserConnection(
                connection_name=connection.name if conn else 'Unknown',
                username=conn.username,
                identifier=connection.identifier,
                last_active=parse_last_active(conn.start_date)
            )

        users = list(map(_map_connection, active_connections))

        return ConnectionTimeline(
            fetched_at=datetime.now(UTC),
            users=users,
            total=len(users),
        )

    def encode_token(self, identifier: str, char: Literal['a', 'c']) -> str:
        '''
        Encodes a connection or active instance identifier, no documentation
        exists online for this and apparently this is the only working method.

        Parameters
        ----------
        identifier : str
        char : Literal[&#39;a&#39;, &#39;c&#39;]

        Returns
        -------
        str
        '''
        raw = f'{identifier}\u0000{char}\u0000{self.api_spec.data_source}'
        encoded = base64.b64encode(raw.encode('utf-8', 'strict')).decode()
        return encoded.removesuffix('=').removesuffix('=')



    async def get_connectable_url(self, connection_ids: list[str]) -> str:
        '''
        Generates a Guacamole URL that can be used to connect to one or more
        connections or active instances. The oldest active instance for each
        connection is preferred, otherwise the connection itself is used.

        Parameters
        ----------
        connection_ids : list[str]

        Returns
        -------
        str
            A URL that can be used to connect to the specified connections
            or active instances.
        '''
        response = await guac_client.list_active_connections(self.api_spec)

        oldest: dict[str, ConnectionInstance] = {}
        for instance_json in response.values():
            instance = ConnectionInstance.convert(instance_json)
            oldest_instance = oldest.setdefault(
                instance.connection_identifier,
                instance
            )

            if instance.start_date < oldest_instance.start_date:
                oldest[instance.connection_identifier] = instance

        parts = []
        for conn_id in connection_ids:
            if oldest_instance := oldest.get(conn_id):
                parts.append(self.encode_token(oldest_instance.identifier, 'a'))
            else:
                parts.append(self.encode_token(conn_id, 'c'))

        parts_path = '.'.join(parts)
        return f'{self.api_spec.client.base_url}/#/client/{parts_path}'

    async def kill_connections(self, connection_ids: list[str]):
        return await guac_client.kill_connections(self.api_spec, connection_ids)

    async def _fetch_active_instances(self) -> dict[str, ConnectionInstance]:
        '''
        Awaitable coroutine to fetch and map all active connections

        Returns
        -------
        dict[str, ConnectionInstance]
        '''
        response = await guac_client.list_active_connections(self.api_spec)
        return dict(map(
            _map_active_connections,
            response.items()
        ))

    async def get_connection_sessions(
        self,
        connection_id: str,
        active_instances: list[ConnectionInstance] | None = None
    ) -> ConnectionSessions:
        '''
        Retrieves the details for a specific connection, including any active
        instances if provided or fetches them if not.

        Parameters
        ----------
        connection_id : str
        active_instances : list[ConnectionInstance] | None, optional
            If provided, these active instances will be filtered for the
            specified connection identifier, by default None

        Returns
        -------
        ConnectionSessions
        '''
        if active_instances is None:
            raw_conn, instances = await asyncio.gather(*(
                guac_client.get_connection(self.api_spec, connection_id),
                self._fetch_active_instances()
            ))
        else:
            raw_conn = await guac_client.get_connection(self.api_spec, connection_id)

        connection = Connection.convert(raw_conn)

        instances = list(filter(
            lambda inst: inst.connection_identifier == connection.identifier,
            active_instances or []
        ))

        return ConnectionSessions(
            connection=connection,
            instances=instances,
        )


    async def get_live_connections(self) -> LiveConnections:
        '''
        Retrieves all live connections and their details

        Returns
        -------
        LiveConnections
        '''
        instances = await guac_client.list_active_connections(self.api_spec)
        instances = list(map(
            ConnectionInstance.convert,
            instances.values()
        ))

        results = LiveConnections()
        for instance in instances:
            conn_id = instance.connection_identifier
            if conn_id in results.sessions:
                continue

            details = await self.get_connection_sessions(
                instance.connection_identifier,
                active_instances=instances
            )

            results.sessions[conn_id] = details
            results.total_connections += len(details.instances)

        return results

