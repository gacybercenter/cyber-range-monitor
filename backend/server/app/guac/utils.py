from __future__ import annotations

import base64
import time
from datetime import UTC, datetime
from typing import Literal

from server.app.guac.client.daos import Connection, ConnectionInstance


def parse_guac_time(last_active: int | None) -> datetime:
    '''
    Gets the datetime for the `lastActive` field, which is in epoch seconds

    Parameters
    ----------
    last_active : int | None
        The last active time in epoch milliseconds

    Returns
    -------
    datetime
    '''
    if last_active is not None:
        last_active_int = int(last_active)
        if last_active_int > 1e10:
            last_active_int = last_active_int // 1000
    else:
        last_active_int = time.time()

    try:
        dt = datetime.fromtimestamp(last_active_int, tz=UTC)
    except Exception:
        dt = datetime.now(UTC)

    return dt


def map_instances(key_value_pair: tuple[str, dict]) -> tuple[str, ConnectionInstance]:
    '''
    Maps `list_active_connections` response key-value pair to
    a dictionary of ConnectionInstance objects.
    '''
    key, value = key_value_pair
    return key, ConnectionInstance.convert(value)


def map_connections(key_value_pair: tuple[str, dict]) -> tuple[str, ConnectionInstance]:
    '''
    Maps a key-value pair from the active connections API response to a
    ConnectionInstance object.

    Parameters
    ----------
    key_value_pair : tuple[str, dict]
        A key-value pair from the active connections API response where the key
        is the connection instance identifier and the value is the connection
        instance details.

    Returns
    -------
    ConnectionInstance
    '''
    key, value = key_value_pair
    return key, ConnectionInstance.convert(value)


def get_connections_map(response: dict) -> dict[str, Connection]:
    '''
    Converts a response dictionary to a dictionary of Connection objects.

    Parameters
    ----------
    response : dict
        The response dictionary from the connections API.

    Returns
    -------
    dict[str, Connection]
    '''

    def _map_func(item: tuple[str, dict]) -> tuple[str, Connection]:
        key, value = item
        return key, Connection.convert(value)

    return dict(map(_map_func, response.items()))


def to_instance_list(response: dict) -> list[ConnectionInstance]:
    instances = map(ConnectionInstance.convert, response.values())
    return list(instances)


def to_instance_map(response: dict) -> dict[str, ConnectionInstance]:
    return dict(map(map_instances, response.items()))


def to_connection_list(response: dict) -> list[Connection]:
    return list(map(Connection.convert, response.values()))


def filter_instance_by_connection_id(
    instances: list[ConnectionInstance], connection_id: str
) -> list[ConnectionInstance]:
    def _filter_fn(instance: ConnectionInstance) -> bool:
        return instance.connection_identifier == connection_id

    filtered = filter(_filter_fn, instances or [])
    return list(filtered)


def guac_urlencode(identifier: str, char: Literal['a', 'c'], data_source: str) -> str:
    '''
    Encodes a connection or active instance identifier, no documentation
    exists online for this and apparently this is the only working method.

    Parameters
    ----------
    identifier : str
        The connection or active instance identifier
    char : Literal[&#39;a&#39;, &#39;c&#39;]
        &#39;a&#39; for active connection, &#39;c&#39; for connection
    data_source : str
        The data source identifier

    Returns
    -------
    str
    '''
    raw = f'{identifier}\u0000{char}\u0000{data_source}'
    encoded = base64.b64encode(raw.encode('utf-8', 'strict')).decode()
    return encoded.removesuffix('=').removesuffix('=')


def map_instances_by_oldest(response: dict) -> dict[str, ConnectionInstance]:
    '''
    From a response of active connection instances, get the oldest instance
    for each connection identifier.

    Parameters
    ----------
    response : dict
        The response dictionary from the active connections API.

    Returns
    -------
    dict[str, ConnectionInstance]
    '''
    oldest: dict[str, ConnectionInstance] = {}
    for instance_json in response.values():
        instance = ConnectionInstance.convert(instance_json)
        conn_id = instance.connection_identifier
        oldest_instance = oldest.setdefault(conn_id, instance)

        if instance.start_date < oldest_instance.start_date:
            oldest[conn_id] = instance

    return oldest
