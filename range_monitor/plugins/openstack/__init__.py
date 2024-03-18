"""
OpenStack Monitor
"""
import json
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
    Renders an overview of OpenStack resources

    Returns:
        str: The rendered HTML template for the dashboard overview.
    """

    return render_template('openstack/overview.html')


@bp.route('/instances', methods=['GET'])
@login_required
def instances():
    """
    Renders OpenStack instances.

    Returns:
        str: The rendered HTML template for displaying the instances.
    """

    return render_template('openstack/instances.html')


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


@bp.route('/api/project_data', methods=['GET'])
@login_required
def project_data():
    """
    Retrieve and return data about OpenStack projects.

    Returns:
        dic: A dictionary containing data about projects.
    """

    projects = stack_data.get_projects_data()
    return jsonify(projects)


@bp.route('/<int:instance_id>/instance_timeline', methods=('GET', 'POST'))
@login_required
def instance_timeline(instance_id):
    """
    Renders the timeline of an instance's activityt.

    Returns:
        str: The rendered HTML template for displaying the instance's timeline.
    """

    history = stack_data.get_instance_history(instance_id)
    dataset = parse.format_history(history)

    return render_template('openstack/instance_timeline.html',
                           history=json.dumps(dataset))


@bp.route('/networks', methods=['GET'])
@login_required
def networks():
    """
    Renders the OpenStack networks.
    
    Returns:
        str: The rendered HTML template for displaying the networks.
    """
    return render_template('openstack/networks.html')


@bp.route('/api/network_data')
@login_required
def network_data():
    """
    Retrieve and return the data about OpenStack networks.

    Returns:
        dict: A dictionary containing data about networks.
    """

    networks = stack_data.get_networks_data()

    return jsonify(networks)


@bp.route('/volumes', methods=['GET'])
@login_required
def volumes():
    """
    Renders the OpenStack volumes.

    Returns:
        str: The rendered HTML template for displaying the volumes.
    """
    return render_template('openstack/networks.html')
    

@bp.route('/api/volume_data')
@user_required
def volume_data():
    """
    Renders the OpenStack volumes.

    Returns:
        str: The rendered HTML template for displaying the volumes.
    """
    volumes = stack_data.get_volumes_data()

    return jsonify(volumes)


@bp.route('/network/<int:network_id>', methods=['GET'])
@admin_required
def network_details(network_id):
    """
    Renders details for a specific OpenStack network.

    Returns:
        str: The rendered HTML template for displaying detailed information about the network.
    """
    network_details = stack_data.get_network_details(network_id)

    return render_template('openstack/network_details.html', details=network_details)


@bp.route('/volume/<int:volume_id>', methods=['GET'])
@admin_required
def volume_details(volume_id):
    """
    Renders details for a specific OpenStack volume.

    Returns:
        str: The rendered HTML template for displaying detailed information about the volume.
    """
    volume_details = stack_data.get_volume_details(volume_id)

    return render_template('openstack/volume_details.html', details=volume_details)