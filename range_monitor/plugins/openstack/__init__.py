"""
OpenStack Monitor
"""
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request
from range_monitor.auth import login_required, admin_required, user_required
from . import stack_conn
from . import stack_data
from . import parse

bp = Blueprint('openstack',
               __name__,
               template_folder='./templates',
               static_folder='./static')

@bp.route('/')
@login_required
def overview():
    """
    Renders a general dashboard overview.

    Returns:
        str: The rendered HTML template for the dashboard overview.
    """
    try:
        cpu_usage_data = stack_data.get_cpu_usage()
        memory_usage_data = stack_data.get_memory_usage()
        active_networks_count = stack_data.get_active_networks()
        
        general_data = {
            'active_instances_count': len(stack_data.get_active_instances()),
            'active_networks_count': active_networks_count,
            'cpu_usage_data': cpu_usage_data,
            'memory_usage_data': memory_usage_data
        }

        return render_template('openstack/overview.html', data=general_data)
    except Exception as e:
        logging.error(f"Error rendering overview: {e}")
        return render_template('openstack/overview.html', error=str(e))


@bp.route('/topology', methods=['GET'])
@login_required
def topology():
    """
    Renders the OpenStack topology.

    Returns:
        str: The rendered HTML template for the topology.
    """
    return render_template('openstack/topology.html')

@bp.route('/api/topology_data', methods=['GET'])
@login_required
def topology_data():
    """
    Endpoint to retrieve topology data.
    """
    try:
        topology_data = stack_data.get_topology_data()
        return jsonify(topology_data)
    except Exception as e:
        logging.error(f"Error fetching topology data: {e}")
        return jsonify({"error": str(e)}), 500

@bp.route('/active_instances', methods=['GET'])
@login_required
def active_instances():
    """
    Renders active OpenStack instances.

    Returns:
        str: The rendered HTML template for displaying the active instances.
    """
    active_instances = stack_data.get_active_instances()
    return render_template('openstack/active_instances.html', instances=active_instances)

@bp.route('/networks', methods=['GET'])
@login_required
def networks():
    """
    Renders the OpenStack networks.
    
    Returns:
        str: The rendered HTML template for displaying the networks.
    """
    networks = stack_data.get_networks_data()
    return render_template('openstack/networks.html', networks=networks)

@bp.route('/volumes', methods=['GET'])
@login_required
def volumes():
    """
    Renders the OpenStack volumes.

    Returns:
        str: The rendered HTML template for displaying the volumes.
    """
    volumes = stack_data.get_volumes_data()
    return render_template('openstack/volumes.html', volumes=volumes)

@bp.route('/performance', methods=['GET'])
@login_required
def performance():
    """
    Renders OpenStack performance.

    Returns:
        str: The rendered HTML template for displaying performance.
    """
    performance_data = stack_data.get_performance_data()
    return render_template('openstack/performance.html', performance=performance_data)

@bp.route('/active_connections', methods=['GET'])
@login_required
def active_connections_data():
    """
    Renders the active connections.

    Returns:
        str: The rendered HTML template for displaying the active connections.
    """
    active_connections = stack_data.get_active_conns()
    return render_template('openstack/active_connections.html', connections=active_connections)

@bp.route('/active_users', methods=['GET'])
@login_required
def active_users():
    """
    Renders the active users.

    Returns:
        str: The rendered HTML template for displaying the active users.
    """
    active_users = stack_data.get_active_users()
    return render_template('openstack/active_users.html', users=active_users)

@bp.route('/connections_graph', methods=['GET'])
@login_required
def connections_graph():
    """
    Renders the connections graph.

    Returns:
        str: The rendered HTML template for displaying the connections graph.
    """
    connections_graph = stack_data.get_connections_graph()
    return render_template('openstack/connections_graph.html', graph=connections_graph)

@bp.route('/timeline', methods=['GET', 'POST'])
@login_required
def connection_timeline():
    """
    Renders the connection timeline page and fetches the history if a connection is selected.

    Returns:
        str: The rendered HTML template for displaying the connection timeline.
    """
    connections = stack_data.get_active_connections()
    history = None

    if request.method == 'POST':
        conn_identifier = request.form.get('conn_identifier')
        if conn_identifier:
            history = stack_data.get_connection_history(conn_identifier)
            print("History data:", history)  # Log the history data
            history = parse.format_history(history)

    return render_template('openstack/timeline.html', connections=connections, history=json.dumps(history) if history else None)

@bp.route('/select_connection', methods=['GET'])
@login_required
def select_connection():
    """
    Renders the page to select a connection to view its timeline.

    Returns:
        str: The rendered HTML template for selecting a connection.
    """
    connections = stack_data.get_active_connections()
    return render_template('openstack/select_connection.html', connections=connections)

@bp.route('/connections', methods=['GET'])
@login_required
def connections_list():
    """
    Renders the page listing all active connections.

    Returns:
        str: The rendered HTML template for listing connections.
    """
    connections = stack_data.get_active_connections()
    return render_template('openstack/list_connections.html', connections=connections)

@bp.route('/input_connection', methods=['GET'])
@login_required
def input_connection():
    """
    Renders the page to input a connection ID.

    Returns:
        str: The rendered HTML template for inputting a connection ID.
    """
    return render_template('openstack/input_connection.html')

@bp.route('/api/active_networks', methods=['GET'])
@login_required
def api_active_networks():
    try:
        active_networks_count = stack_data.get_active_networks()
        return jsonify(active_networks_count)
    except Exception as e:
        logging.error(f"Error fetching active networks count: {e}")
        return jsonify({"error": str(e)}), 500
