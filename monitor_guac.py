"""
Guacamole Monitor
"""

import json
import yaml
from flask import Flask, render_template
from guacamole import session as guac_connection

app = Flask(__name__, template_folder='templates')

with open('config.yaml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)


gconn = guac_connection(config['host'],
                        config['data_source'],
                        config['username'],
                        config['password'])


@app.route('/')
def index():
    """
    A function that serves as the handler for the root URL ("/"). 
    It returns the rendered template named "index.html".
    """
    return render_template('index.html')


@app.route('/active_connections', methods=['GET'], defaults={'timeout': None})
@app.route('/active_connections/<timeout>', methods=['GET'])
def active_connections_route(timeout=None):
    """
    Renders the active connections from the server.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """

    active_instances = json.loads(
        gconn.list_connections(active=True)
    )
    active_data = [
        {
            'data': json.loads(
                gconn.detail_connection(
                    instance['connectionIdentifier']
                )
            ),
            'username': instance['username'],
        }
        for instance in active_instances.values()
    ]

    active_conns = {}

    for conn in active_data:
        conn_name = conn['data'].get('name')
        column_name = conn_name.split('.')[0]
        active_conns.setdefault(
            column_name, []
        ).append({
            'connection': conn_name,
            'username': conn['username']
        })

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

    total_active_users = len(active_users)

    return render_template('active_users.html',
                           active_users=active_users,
                           total_active_users=total_active_users)


if __name__ == '__main__':
    app.run(debug=True)
