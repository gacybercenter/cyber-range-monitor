from dataclasses import dataclass
from typing import Any

import httpx

from range_monitor.guac.api import utils as api_utils


@dataclass(slots=True)
class GuacamoleClientSpec:
    client: httpx.AsyncClient
    data_source: str
    sessions_url: str


    @property
    def tunnels(self) -> str:
        return '/api/session/tunnels'

    @property
    def history(self) -> str:
        return f'{self.sessions_url}/history'

    @property
    def users(self) -> str:
        return f'{self.sessions_url}/users'

    @property
    def connections(self) -> str:
        return f'{self.sessions_url}/connections'

    @property
    def connection_groups(self) -> str:
        return f'{self.sessions_url}/connectionGroups'

    @property
    def usergroups(self) -> str:
        return f'{self.sessions_url}/userGroups'

    @property
    def sharing_profiles(self) -> str:
        return f'{self.sessions_url}/sharingProfiles'

    @property
    def active_connections(self) -> str:
        return f'{self.sessions_url}/activeConnections'

    @property
    def client_token(self) -> str:
        '''
        See `range_monitor.sources.auth_schemes._guac_token`
        for full type definition.

        Returns
        -------
        str
        '''
        return self.client.auth.scheme.token # type: ignore

# keep in mind, the range_monitor (unless scope has changed),
# should be primarily read-only

def create_client_spec(
    client: httpx.AsyncClient,
    data_source: str = 'default'
) -> GuacamoleClientSpec:
    sessions_url = f'/api/session/data/{data_source}'
    return GuacamoleClientSpec(
        client=client,
        data_source=data_source,
        sessions_url=sessions_url
    )

async def list_extensions(spec: GuacamoleClientSpec):
    path = f'{spec.sessions_url}/extensions'
    return await api_utils.fetch(path, spec.client)

async def get_self(spec: GuacamoleClientSpec):
    path = f'{spec.sessions_url}/self'
    return await api_utils.fetch(path, spec.client)


async def list_users_history(spec: GuacamoleClientSpec):
    path = f'{spec.history}/users'
    return await api_utils.fetch(path, spec.client, stream=True)

async def list_connections_history(spec: GuacamoleClientSpec):
    path = f'{spec.history}/connections'
    return await api_utils.fetch(path, spec.client, stream=True)

async def list_users(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.users, spec.client, stream=True)

async def get_user(spec: GuacamoleClientSpec, username: str):
    path = f'{spec.users}/{username}'
    return await api_utils.fetch(path, spec.client)

async def get_user_permissions(spec: GuacamoleClientSpec, username: str):
    path = f'{spec.users}/{username}/permissions'
    return await api_utils.fetch(path, spec.client)

async def get_user_effective_permissions(spec: GuacamoleClientSpec, username: str):
    path = f'{spec.users}/{username}/effectivePermissions'
    return await api_utils.fetch(path, spec.client)

async def get_user_history(spec: GuacamoleClientSpec, username: str):
    path = f'{spec.users}/{username}/history'
    return await api_utils.fetch(path, spec.client)


async def list_usergroups(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.usergroups, spec.client, stream=True)

async def get_usergroup(spec: GuacamoleClientSpec, group_name: str):
    path = f'{spec.usergroups}/{group_name}'
    return await api_utils.fetch(path, spec.client)

async def get_usergroup_permissions(spec: GuacamoleClientSpec, group_name: str):
    path = f'{spec.usergroups}/{group_name}/permissions'
    return await api_utils.fetch(path, spec.client)

async def list_connections(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.connections, spec.client, stream=True)

async def list_active_connections(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.active_connections, spec.client, stream=True)

async def get_connection(spec: GuacamoleClientSpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}'
    return await api_utils.fetch(path, spec.client)

async def get_connection_history(spec: GuacamoleClientSpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}/history'
    return await api_utils.fetch(path, spec.client, stream=True)

async def get_connection_parameters(spec: GuacamoleClientSpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}/parameters'
    return await api_utils.fetch(path, spec.client)

async def list_sharing_profiles(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.sharing_profiles, spec.client, stream=True)

async def get_sharing_profile(spec: GuacamoleClientSpec, profile_id: str):
    path = f'{spec.sharing_profiles}/{profile_id}'
    return await api_utils.fetch(path, spec.client)

async def get_sharing_profile_parameters(spec: GuacamoleClientSpec, profile_id: str):
    path = f'{spec.sharing_profiles}/{profile_id}/parameters'
    return await api_utils.fetch(path, spec.client)

async def list_connection_groups(spec: GuacamoleClientSpec):
    return await api_utils.fetch(spec.connection_groups, spec.client, stream=True)

async def get_connection_group(spec: GuacamoleClientSpec, group_id: str):
    path = f'{spec.connection_groups}/{group_id}'
    return await api_utils.fetch(path, spec.client)

async def get_connection_group_tree(spec: GuacamoleClientSpec, group_id: str = 'ROOT'):
    path = f'{spec.connection_groups}/{group_id}/tree'
    return await api_utils.fetch(path, spec.client)


def _map_kill_connections_body(id: str) -> dict[str, str]:
    return {
        'op': 'remove',
        'path': f'/{id}',
    }



async def kill_connections(
    spec: GuacamoleClientSpec,
    connection_ids: list[str]
) -> dict | Any:
    body = list(map(_map_kill_connections_body, connection_ids))

    response = await spec.client.patch(
        spec.active_connections,
        json=body,
        headers={'Content-Type': 'application/json'}
    )
    response.raise_for_status()
    return response.json()


