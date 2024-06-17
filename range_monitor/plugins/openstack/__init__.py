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
        # Fetch general overview data, if needed
    general_data = {
        'active_instances_count': len(stack_data.get_active_instances()),
        # Add other general overview metrics as needed
    }
    
    return render_template('openstack/overview.html', data=general_data)

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

@bp.route('/timeline', methods=['GET'])
@login_required
def timeline():
    """
    Renders the timeline.

    Returns:
        str: The rendered HTML template for displaying the timeline.
    """
    timeline = stack_data.get_timeline()
    return render_template('openstack/timeline.html', timeline=timeline)