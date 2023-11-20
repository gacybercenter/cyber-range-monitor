"""
Helper functions
"""

from time import time

def extract_connections(obj: dict) -> (list, dict):
    """
    Recursively walks through an object and extracts connection groups,
    connections, and sharing groups.

    Parameters:
    obj (dict): The object to extract groups and connections from.

    Returns:
    list: The extracted connection groups, connections, and sharing groups.
    """

    conns = []
    active_conn_sum = 0

    if isinstance(obj, dict):
        if obj.get('name') and obj.get('parentIdentifier'):
            conn = obj.copy()
            conn['activeConnections'] = int(conn['activeConnections'])
            if conn.get('childConnectionGroups'):
                child_conns, child_sum = extract_connections(conn['childConnectionGroups'])
                conn['activeConnections'] = child_sum
                del conn['childConnectionGroups']
                conns += child_conns

            if conn.get('childConnections'):
                child_conns, child_sum = extract_connections(conn['childConnections'])
                conn['activeConnections'] += child_sum
                del conn['childConnections']
                conns += child_conns

            conns.append(conn)
            active_conn_sum += conn.get('activeConnections', 0)

        else:
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    child_conns, child_sum = extract_connections(value)
                    conns += child_conns
                    active_conn_sum += child_sum

    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                child_conns, child_sum = extract_connections(item)
                conns += child_conns
                active_conn_sum += child_sum

    return conns, active_conn_sum


def remove_empty(obj: object) -> object:
    """
    Recursively removes None and empty values from a dictionary or a list.

    obj:
    dictionary (dict or list): The dictionary or list to remove None and empty values from.

    Returns:
    dict or list: The dictionary or list with None and empty values removed.
    """
    if isinstance(obj, dict):
        return {
            key: remove_empty(value)
            for key, value in obj.items()
            if value
        }
    if isinstance(obj, list):
        return [
            remove_empty(item)
            for item in obj
            if item
        ]

    return obj


def format_history(history: list) -> list:
    """
    Formats the history of a connection.
    """

    timestamps = []
    users = {}

    for conn in history:
        users.setdefault(
            conn['username'], []
        )

    for conn in history:
        username = conn['username']
        start_date = conn['startDate']
        if conn['endDate']:
            end_date = conn['endDate']
        else:
            end_date = round(time() * 1000)

        for user, value in users.items():
            if user == username:
                value.append(
                    (end_date - start_date) / 60000
                )
            else:
                value.append(None)

        timestamps.append(
            conn['startDate']
        )

    dataset = {
        "labels": timestamps,
        "datasets": [
            {
                "label": username,
                "data": intervals,
            }
            for username, intervals in users.items()
        ]
    }

    return dataset
