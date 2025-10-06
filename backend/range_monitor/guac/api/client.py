import base64

import httpx

from range_monitor.guac.api.dtos import (
    Connection,
    ConnectionInstance,
    GuacUser,
    HistoryEntry,
)
from range_monitor.utils.decorators import retry_request

# list_active_connections
# list_connections
# list_connection_group_connections
# detail_user
# kill_active_connections

@retry_request()
async def get_json(url: str, client: httpx.AsyncClient) -> dict:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


SEP = '\u0000'

def guac_urlencode(
    datasource: str,
    mode: str,
    identifier: str
) -> str:
    raw = f'{identifier}{SEP}{mode}{SEP}{datasource}'.encode('utf-8', 'strict')
    return base64.b64encode(raw).decode('ascii').rstrip('=')


def _oldest_connection_instance(
    instances: list[ConnectionInstance],
    connection_id: str
) -> ConnectionInstance | None:

    def _by_id(inst: ConnectionInstance) -> bool:
        return inst.connection_identifier == connection_id

    matches = filter(_by_id, instances)

    return min(matches, key=lambda inst: inst.start_date)


def build_connectable_url(
    identifiers: list[str],
    active_connections: list[ConnectionInstance],
    hostname: str,
) -> str:
    parts: list[str] = []
    for id in identifiers:
        oldest = _oldest_connection_instance(active_connections, id)
        if oldest:
            segment = guac_urlencode(hostname, 'a', oldest.identifier,)
        else:
            segment = guac_urlencode(hostname, 'c', id)

        parts.append(segment)

    path = '.'.join(parts)
    return f'{hostname}/#/client/{path}'

class GuacamoleAPI:

    def __init__(
        self,
        *,
        client: httpx.AsyncClient,
        data_source: str,
    ) -> None:
        self.client: httpx.AsyncClient = client
        self.data_source: str = data_source

    @property
    def sessions_url(self) -> str:
        return f'/api/session/data/{self.data_source}'

    @property
    def hostname(self) -> str:
        return str(self.client.base_url)

    def sessionpath(self, *paths: str) -> str:
        return '/'.join((self.sessions_url, *paths))

    async def get_active_connections(self) -> list[ConnectionInstance]:
        response = await get_json(
            self.sessionpath('activeConnections'),
            self.client
        )

        return list(map(ConnectionInstance.convert, response.values()))


    async def get_connections(self) -> list[Connection]:
        response = await get_json(
            self.sessionpath('connections'),
            self.client
        )
        return list(map(Connection.convert, response.values()))


    async def get_connection_group_tree(self) -> dict:
        response_json = await get_json(
            self.sessionpath('connectionGroups', 'ROOT', 'tree'),
            self.client
        )
        response_json.pop('attributes', None)
        response_json.update({
            'name': self.hostname,
        })
        return response_json

    async def get_user(self, username: str) -> GuacUser:
        response = await get_json(
            self.sessionpath('users', username),
            self.client
        )
        return GuacUser.convert(response)

    async def kill_connections(self, connection_ids: list[str]) -> dict:

        json_data = []
        for id in connection_ids:
            json_data.append({
                'op': 'remove',
                'path': f'/{id}',
            })

        response = await self.client.patch(
            self.sessionpath('activeConnections'),
            json=json_data,
            headers={
                'Content-Type': 'application/json'
            }
        )
        response.raise_for_status()
        return response.json()

    async def get_connection_history(self, connection_id: str) -> list[HistoryEntry]:
        response_json = await get_json(
            self.sessionpath('connections', connection_id, 'history'),
            self.client
        )
        return list(map(HistoryEntry.convert, response_json))

    async def create_connectable_url(self, identifiers: list[str]) -> str:
        active = await self.get_active_connections()
        return build_connectable_url(
            identifiers,
            active,
            self.hostname
        )

    async def get_token(self) -> str:
        return await self.client.auth.get_token() # type: ignore

    