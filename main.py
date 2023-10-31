"""
Guacamole Monitor
"""

import datetime
from flask import Flask, render_template, jsonify, request
import guac_data
import parse

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """
    A function that serves as the handler for the root URL ("/"). 
    It returns the rendered template named "index.html".
    """
    return render_template('index.html')


@app.route('/active_connections', methods=['GET'])
def active_connections_route():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    active_conns = guac_data.get_active_connections()

    return render_template('active_connections.html',
                           active_conns=active_conns)


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


@app.route('/topology')
def topology_route():
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """
    return render_template('topology.html')


@app.route('/api/graph_data')
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

    active_conns = guac_data.get_active_instances()
    date = datetime.datetime.now().strftime("%H:%M:%S")

    graph_data = {
        'date': date,
        'conns': len(active_conns)
    }

    return jsonify(graph_data)


@app.route('/api/topology_data')
def get_tree_data():
    """
    Retrieves the tree data for the topology API.

    Parameters:
        timeout (float, optional): The timeout value in seconds for the request. Defaults to None.

    Returns:
        Response: The JSON response containing the extracted connections.
    """

    conn_tree = guac_data.get_tree_data()
    connections = parse.extract_connections(conn_tree)
    connections = guac_data.resolve_users(connections)

    return jsonify(connections)


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
