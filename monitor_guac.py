import guacamole
import json
import yaml
from flask import Flask, render_template

app = Flask(__name__)

with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

GUAC_URL = config['guacamole_url']
USERNAME = config['username']
PASSWORD = config['password']
API_TOKEN = config['api_token']

session = guacamole.session(GUAC_URL, "mysql", USERNAME, PASSWORD)

@app.route('/active_connections', methods=['GET'], defaults={'timeout': None})
@app.route('/active_connections/<timeout>', methods=['GET'])
def active_connections_route(timeout):
    sessions = json.loads(session.list_connections())
    active_connections = {}

    for identifier, connection in sessions.items():
        if connection.get("activeConnections", 0) == 1:
            name = connection.get('name')
            column_name = name.split('.')[0]  # Get the part before the first "."
            active_connections.setdefault(column_name, []).append(name)

    total_active_connections = sum(len(names) for names in active_connections.values())
    
    return render_template('active_connections.html', active_connections=active_connections, total_active_connections=total_active_connections)

if __name__ == '__main__':
    app.run(debug=True)
