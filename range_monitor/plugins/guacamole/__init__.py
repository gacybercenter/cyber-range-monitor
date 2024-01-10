"""
Guacamole Monitor
"""
import json
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from range_monitor.auth import login_required, admin_required, user_required
from . import guac_data
from . import parse

bp = Blueprint('guacamole',
               __name__,
               template_folder='./templates',
               static_folder='./static')

@bp.route('/')
@login_required
def topology():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    return render_template('guac/topology.html')


@bp.route('/active_connections', methods=['GET'])
@login_required
def active_connections():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    return render_template('guac/active_connections.html')


@bp.route('/active_users', methods=['GET'])
@login_required
def active_users():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    identifier = 1
    users = guac_data.get_active_users(identifier)

    return render_template('guac/active_users.html',
                           active_users=users)


@bp.route('/<int:conn_identifier>/connection_timeline', methods=('GET', 'POST'))
@login_required
def connection_timeline(conn_identifier):
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    identifier = 1
    history = guac_data.get_connection_history(identifier,
                                               conn_identifier)
    dataset = parse.format_history(history)

    return render_template('guac/timeline.html',
                           history=json.dumps(dataset))


@bp.route('/api/conns_data')
@login_required
def get_graph_data():
    """
    Retrieve and return the graph data.

    Args:
        timeout (Optional[int]): The timeout value for the data retrieval.

    Returns:
        dict: A dictionary containing the graph data with the following keys:
            - date (str): The current date and time in the format "HH:MM:SS".
            - conns (int): The number of active connections.

    Raises:
        None
    """

    identifier = 1
    date = datetime.now().strftime("%H:%M:%S")
    active_conns = guac_data.get_active_conns(identifier)

    graph_data = {
        'date': date,
        'amount': len(active_conns),
        'conns': active_conns
    }

    return jsonify(graph_data)


last_conn_tree = {}
last_connections = {}
last_conn_sum = 0

@bp.route('/api/topology_data')
@login_required
def get_tree_data():
    """
    Retrieves the tree data for the topology API.

    Parameters:
        timeout (float, optional): The timeout value in seconds for the request. Defaults to None.

    Returns:
        Response: The JSON response containing the extracted connections.
    """

    global last_conn_tree
    global last_connections
    global last_conn_sum

    identifier = 1
    conn_tree = guac_data.get_tree_data(identifier)

    if last_conn_tree != conn_tree:
        connections, conn_sum = parse.extract_connections(conn_tree)
        connections = guac_data.resolve_users(identifier, connections)
        last_conn_tree = conn_tree
        last_connections = connections
        last_conn_sum = conn_sum

    data = {
        'nodes': last_connections,
        'total': last_conn_sum
    }

    return jsonify(data)


@bp.route('/connect-to-node', methods=['POST'])
@user_required
def connect_to_node():
    """
    Connects to a node.

    Args:
        None

    Returns:
        A JSON response with an empty dictionary.
    """

    identifier = 1
    data = request.get_json()
    conn_identifiers = data['identifiers']

    url = guac_data.get_connection_link(identifier, conn_identifiers)

    return jsonify({'url': url})


@bp.route('/kill-connections', methods=['POST'])
@admin_required
def kill_node_connections():
    """
    Connects to a node.

    Args:
        None

    Returns:
        A JSON response with an empty dictionary.
    """

    identifier = 1
    data = request.get_json()
    conn_identifiers = data['identifiers']

    response = guac_data.kill_connection(identifier, conn_identifiers)

    return jsonify(response)
