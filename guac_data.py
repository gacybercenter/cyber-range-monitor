"""
Gets data from Guacamole
"""

import json
from conns import guac_connect

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

    active_instances = json.loads(
        gconn.list_connections(active=True)
    )
    connections = json.loads(
        gconn.list_connections()
    )
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

    active_instances = json.loads(gconn.list_connections(active=True))
    active_usernames = set(
        instance['username']
        for instance in active_instances.values()
    )
    active_user_data = [
        json.loads(gconn.detail_user(user))
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
