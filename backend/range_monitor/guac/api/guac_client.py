from typing import Any

from range_monitor.guac.api.spec import GuacamoleAPISpec
from range_monitor.utils import httpx_utils


async def list_extensions(spec: GuacamoleAPISpec):
    path = f'{spec.sessions_url}/extensions'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_self(spec: GuacamoleAPISpec):
    path = f'{spec.sessions_url}/self'
    return await httpx_utils.fetch_json(path, spec.client)


def list_users_history(spec: GuacamoleAPISpec):
    path = f'{spec.history}/users'
    return httpx_utils.fetch_json_stream(
        spec.client,
        path,
    )

def list_connections_history(spec: GuacamoleAPISpec):
    path = f'{spec.history}/connections'
    return httpx_utils.fetch_json_stream(
        spec.client,
        path,
    )

async def list_users(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.users, spec.client, stream=True)

async def get_user(spec: GuacamoleAPISpec, username: str):
    path = f'{spec.users}/{username}'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_user_permissions(spec: GuacamoleAPISpec, username: str):
    path = f'{spec.users}/{username}/permissions'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_user_effective_permissions(spec: GuacamoleAPISpec, username: str):
    path = f'{spec.users}/{username}/effectivePermissions'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_user_history(spec: GuacamoleAPISpec, username: str):
    path = f'{spec.users}/{username}/history'
    return await httpx_utils.fetch_json(path, spec.client)


async def list_usergroups(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.usergroups, spec.client, stream=True)

async def get_usergroup(spec: GuacamoleAPISpec, group_name: str):
    path = f'{spec.usergroups}/{group_name}'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_usergroup_permissions(spec: GuacamoleAPISpec, group_name: str):
    path = f'{spec.usergroups}/{group_name}/permissions'
    return await httpx_utils.fetch_json(path, spec.client)

async def list_connections(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.connections, spec.client, stream=True)

async def list_active_connections(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.active_connections, spec.client, stream=True)

async def get_connection(spec: GuacamoleAPISpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_connection_history(spec: GuacamoleAPISpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}/history'
    return await httpx_utils.fetch_json(path, spec.client, stream=True)

async def get_connection_parameters(spec: GuacamoleAPISpec, connection_id: str):
    path = f'{spec.connections}/{connection_id}/parameters'
    return await httpx_utils.fetch_json(path, spec.client)

async def list_sharing_profiles(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.sharing_profiles, spec.client, stream=True)

async def get_sharing_profile(spec: GuacamoleAPISpec, profile_id: str):
    path = f'{spec.sharing_profiles}/{profile_id}'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_sharing_profile_parameters(spec: GuacamoleAPISpec, profile_id: str):
    path = f'{spec.sharing_profiles}/{profile_id}/parameters'
    return await httpx_utils.fetch_json(path, spec.client)

async def list_connection_groups(spec: GuacamoleAPISpec):
    return await httpx_utils.fetch_json(spec.connection_groups, spec.client, stream=True)

async def get_connection_group(spec: GuacamoleAPISpec, group_id: str):
    path = f'{spec.connection_groups}/{group_id}'
    return await httpx_utils.fetch_json(path, spec.client)

async def get_connection_group_tree(spec: GuacamoleAPISpec, group_id: str = 'ROOT'):
    path = f'{spec.connection_groups}/{group_id}/tree'
    return await httpx_utils.fetch_json(path, spec.client)


def _map_kill_connections_body(id: str) -> dict[str, str]:
    return {
        'op': 'remove',
        'path': f'/{id}',
    }



async def kill_connections(
    spec: GuacamoleAPISpec,
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


