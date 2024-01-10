"""
Gets data from Guacamole
"""

from time import sleep
from base64 import b64encode
from . import guac_conn


def get_active_instances(identifier: int):
    """
    Retrieves a list of active connections.

    Returns:
        dict: A dictionary containing active connections grouped by column name.
            Each key represents a column name and its corresponding value is a
            list of dictionaries, each containing the connection name and the
            username associated with that connection.
    """

    gconn = guac_conn.guac_connect(identifier)

    active_instances = gconn.list_active_connections()

    return active_instances


def get_active_conns(identifier: int):
    """
    Retrieves a list of active connections.

    Returns:
        dict: A dictionary containing active connections grouped by column name.
            Each key represents a column name and its corresponding value is a
            list of dictionaries, each containing the connection name and the
            username associated with that connection.
    """

    gconn = guac_conn.guac_connect(identifier)

    active_instances = gconn.list_active_connections().values()
    sleep(0.02)
    connections = gconn.list_connections()
    connection_ids = connections.keys()

    active_data = [
        {
            'connection': connections[
                instance['connectionIdentifier']
            ]['name'],
            'username': instance['username'],
        }
        for instance in active_instances
        if instance['connectionIdentifier'] in connection_ids
    ]

    return active_data


def get_active_users(identifier: int):
    """
    Get the active users from the guacamole connection.

    Returns:
        active_users (dict): A dictionary containing the active users.
            Grouped by column user organization.
    """

    gconn = guac_conn.guac_connect(identifier)

    active_instances = gconn.list_active_connections()
    active_usernames = set(
        instance['username']
        for instance in active_instances.values()
    )
    active_user_data = [
        gconn.detail_user(user)
        for user in active_usernames
    ]
    active_users = {}

    for user in active_user_data:
        user_name = user.get('username')
        column_name = user['attributes'].get(
            'guac-organization', 'No Organization'
        )
        active_users.setdefault(
            column_name, []
        ).append(user_name)

    return active_users


def get_tree_data(identifier: int):
    """
    Get the tree data from the guacamole connection.

    Returns:
        tree_data (dict): A dictionary containing the tree data.
            Grouped by column user organization.
    """

    gconn = guac_conn.guac_connect(identifier)

    tree_data = gconn.list_connection_group_connections()

    return tree_data


def resolve_users(identifier: int,
                  connections: list):
    """
    Resolve the users associated with the given connections.

    Parameters:
        connections (list): A list of connection dictionaries.

    Returns:
        connections (list): The updated list of connection dictionaries
            with the 'users' field populated.
    """

    gconn = guac_conn.guac_connect(identifier)

    active_conns = gconn.list_active_connections().values()

    for conn in connections:
        if conn['activeConnections'] > 0:
            conn['users'] = set(
                active_conn['username']
                for active_conn in active_conns
                if active_conn['connectionIdentifier'] == conn['identifier']
            )
            conn['users'] = list(conn['users'])

    return connections


def kill_connection(identifier: int,
                    conn_identifiers: list):
    """
    Kill connections.

    Parameters:
        conn_identifiers (list): The identifiers of the connections to kill.
    """

    if not conn_identifiers:
        return None

    gconn = guac_conn.guac_connect(identifier)

    active_instances = gconn.list_active_connections()

    active_uuids = [
        uuid
        for uuid, instance in active_instances.items()
        if instance['connectionIdentifier'] in conn_identifiers
    ]

    gconn.kill_active_connections(active_uuids)
    return active_uuids


def get_connection_link(identifier: int,
                        conn_identifiers: list):
    """
    Returns a connection link.

    Parameters:
        identifiers (list): The identifiers of the connections to kill.
    """

    gconn = guac_conn.guac_connect(identifier)

    if not conn_identifiers:
        return gconn.host

    active_instances = gconn.list_active_connections()
    host_url = f"{gconn.host}/#/client"
    url_data = []

    for conn_identifier in conn_identifiers:
        oldest_instance = {}
        for instance in active_instances.values():
            is_older_instance = instance['connectionIdentifier'] == conn_identifier and (
                not oldest_instance
                or instance['startDate'] < oldest_instance.get('startDate', 0)
            )
            if is_older_instance:
                oldest_instance = instance

        if oldest_instance:
            uuid = oldest_instance['identifier']
            url_data.append(b64encode(
                    f"{uuid}\u0000a\u0000{gconn.data_source}".encode('utf-8', 'strict')
            ).decode().removesuffix('=').removesuffix('='))
        else:
            url_data.append(b64encode(
                    f"{conn_identifier}\u0000c\u0000{gconn.data_source}".encode('utf-8', 'strict')
            ).decode().removesuffix('=').removesuffix('='))

    url_str = '.'.join(url_data)

    return f"{host_url}/{url_str}"


def get_connection_history(identifier: int,
                           conn_identifier: str):
    """
    Returns a connection link.

    Parameters:
        identifiers (list): The identifiers of the connections to kill.
    """

    gconn = guac_conn.guac_connect(identifier)

    if not conn_identifier:
        return {}

    return gconn.detail_connection(conn_identifier, 'history')
