"""
Guacamole Monitor
"""

import datetime
from flask import Flask, render_template, jsonify, request
from src import guac_data, parse

app = Flask(__name__, template_folder='templates')


@app.route('/')
def topology_route():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    return render_template('index.html')


@app.route('/active_connections', methods=['GET'])
def active_connections_route():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    return render_template('active_connections.html')


@app.route('/active_users', methods=['GET'])
def active_users_route():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    active_users = guac_data.get_active_users()

    return render_template('active_users.html',
                           active_users=active_users)


@app.route('/api/conns_data')
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

    date = datetime.datetime.now().strftime("%H:%M:%S")
    active_conns = guac_data.get_active_conns()

    graph_data = {
        'date': date,
        'amount': len(active_conns),
        'conns': active_conns
    }

    return jsonify(graph_data)


last_conn_tree = {}
last_connections = {}

@app.route('/api/topology_data')
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
    conn_tree = guac_data.get_tree_data()

    if last_conn_tree != conn_tree:
        connections = parse.extract_connections(conn_tree)
        connections = guac_data.resolve_users(connections)
        last_conn_tree = conn_tree
        last_connections = connections

    return jsonify(last_connections)


@app.route('/connect-to-node', methods=['POST'])
def connect_to_node():
    """
    Connects to a node.

    Args:
        None

    Returns:
        A JSON response with an empty dictionary.
    """

    data = request.get_json()
    identifier = data['identifier']

    url = guac_data.get_connection_link(identifier)

    return jsonify({'url': url})


@app.route('/kill-connections', methods=['POST'])
def kill_node_connections():
    """
    Connects to a node.

    Args:
        None

    Returns:
        A JSON response with an empty dictionary.
    """

    data = request.get_json()
    identifier = data['identifier']

    response = guac_data.kill_connection(identifier)

    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            debug=True)
    # app.run(debug=True)
