"""
Guacamole Monitor
"""

import datetime
from flask import Flask, render_template, jsonify
import guac_data
import parse

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """
    A function that serves as the handler for the root URL ("/"). 
    It returns the rendered template named "index.html".
    """
    graph_data = {
        'a': 1,
        'b': 2,
        'c': 3
    }
    return render_template('index.html',
                           max=17000,
                           labels=graph_data.keys(),
                           values=graph_data.values())


@app.route('/active_connections', methods=['GET'], defaults={'timeout': None})
@app.route('/active_connections/<timeout>', methods=['GET'])
def active_connections_route(timeout=None):
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    active_conns = guac_data.get_active_connections()

    return render_template('active_connections.html',
                           active_conns=active_conns,
                           active_conns_length=len(active_conns))


@app.route('/active_users', methods=['GET'], defaults={'timeout': None})
@app.route('/active_users/<timeout>', methods=['GET'])
def active_users_route(timeout=None):
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    active_users = guac_data.get_active_users()

    return render_template('active_users.html',
                           active_users=active_users,
                           total_active_users=len(active_users))


@app.route('/api/graph_data')
def get_graph_data(timeout=None):
    # Retrieve and return the graph data
    active_conns = guac_data.get_active_instances()
    date = datetime.datetime.now().strftime("%H:%M:%S")

    graph_data = {
        'date': date,
        'conns': len(active_conns)
    }

    return jsonify(graph_data)


@app.route('/api/tree_data')
def get_tree_data(timeout=None):
    # Retrieve and return the graph data
    conn_tree = guac_data.get_tree_data()
    connections = parse.extract_connections(conn_tree)

    return jsonify(connections)

if __name__ == '__main__':
    app.run(debug=True)
