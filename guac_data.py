"""
Gets data from Guacamole
"""

from time import sleep
from base64 import b64encode
from conns import guac_connect


def get_active_instances():
    """
    Retrieves a list of active connections.

    Returns:
        dict: A dictionary containing active connections grouped by column name.
            Each key represents a column name and its corresponding value is a
            list of dictionaries, each containing the connection name and the
            username associated with that connection.
    """

    gconn = guac_connect()

    active_instances = gconn.list_active_connections()

    return active_instances


def get_active_connections():
    """
    Retrieves a list of active connections.

    Returns:
        dict: A dictionary containing active connections grouped by column name.
            Each key represents a column name and its corresponding value is a
            list of dictionaries, each containing the connection name and the
            username associated with that connection.
    """

    gconn = guac_connect()

    active_instances = gconn.list_active_connections()
    sleep(0.02)
    connections = gconn.list_connections()

    active_data = [
        {
            'data': connections[
                instance['connectionIdentifier']
            ],
            'username': instance['username'],
        }
        for instance in active_instances.values()
        if instance['connectionIdentifier']
    ]

    active_conns = {}

    for conn in active_data:
        conn_name = conn['data'].get('name', 'No Connection')
        column_name = conn_name.split('.')[0]
        if not column_name:
            column_name = 'No Organization'
        active_conns.setdefault(
            column_name, []
        ).append({
            'connection': conn_name,
            'username': conn['username']
        })

    return active_conns


def get_active_users():
    """
    Get the active users from the guacamole connection.

    Returns:
        active_users (dict): A dictionary containing the active users.
            Grouped by column user organization.
    """

    gconn = guac_connect()

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


def get_tree_data():
    """
    Get the tree data from the guacamole connection.

    Returns:
        tree_data (dict): A dictionary containing the tree data.
            Grouped by column user organization.
    """

    gconn = guac_connect()

    tree_data = gconn.list_connection_group_connections()

    return tree_data


def kill_connection(identifier: str):
    """
    Kill connections.

    Parameters:
        identifiers (list): The identifiers of the connections to kill.
    """

    if not identifier:
        return None

    gconn = guac_connect()

    active_instances = gconn.list_active_connections()

    active_uuids = [
        uuid
        for uuid, instance in active_instances.items()
        if instance['connectionIdentifier'] == identifier
    ]

    return gconn.kill_active_connections(active_uuids)


def get_connection_link(identifier: str):
    """
    Returns a connection link.

    Parameters:
        identifiers (list): The identifiers of the connections to kill.
    """

    gconn = guac_connect()

    if not identifier:
        return gconn.host

    active_instances = gconn.list_active_connections()

    active_uuids = [
        uuid
        for uuid, instance in active_instances.items()
        if instance['connectionIdentifier'] == identifier
    ]

    if active_uuids:
        identifier = active_uuids[0]
        conn_type = '\u0000a\u0000'
    else:
        conn_type = '\u0000c\u0000'

    host_url = f"{gconn.host}/#/client"

    url_data = f"{identifier}{conn_type}{gconn.data_source}"

    encoded_data = b64encode(url_data.encode('utf-8', 'strict')).decode()
    encoded_data = encoded_data.removesuffix('=').removesuffix('=')

    url = f"{host_url}/{encoded_data}"

    return url
