"""
Saltstack plugin for Range Monitor.
"""
import datetime
import json
from flask import Blueprint, render_template, jsonify, request
from range_monitor.auth import login_required, admin_required, user_required
from . import salt_call
from . import salt_conn
from . import parse

bp = Blueprint('salt',
                __name__,
                template_folder='./templates',
                static_folder='./static')

@bp.route('/')
@login_required
def home():
    """
    Renders the active minions from the server.

    Returns:
    str: The rendered HTML template for displaying the active minions.
    """
    hostname = salt_call.salt_conn()['hostname']
    minion_data = salt_conn.get_all_minions()
    if minion_data == False:
        return render_template('salt/salt_error.html')
    return render_template(
        'salt/minions.html',
        hostname = hostname,
        json_data=minion_data,
    )


@bp.route('/graph', methods=['GET'])
@login_required
def events():
    """
    Renders the events from the server.

    Returns:
        str: The rendered HTML template for displaying the events.
    """
    hostname = salt_call.salt_conn()['hostname']
    return render_template(
        'salt/graph.html', 
        hostname = hostname)


@bp.route('/jobs', methods=['GET'])
@login_required
def jobs():
    """
    Renders the active jobs from the server.

    Returns:
        str: The rendered HTML template for displaying the active jobs.
    """
    hostname = salt_call.salt_conn()['hostname']
    json_data = salt_conn.get_all_jobs()
    if json_data == False:
      return render_template('salt/salt_error.html')
    return render_template(
        'salt/jobs.html',
        hostname = hostname, 
        json_data = json_data
    )


@bp.route('/jobs/<string:job_id>', methods=['GET'])
@login_required
def job_page(job_id):
    """
    Renders the template for an advanced view of a minion

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced minion data
    """
    job_json = salt_conn.get_specified_job(job_id)
    return render_template(
        'salt/advanced_job.html', 
        job_id = str(job_id), 
        job_data = job_json
    )


@bp.route('/minions/<string:minion_id>', methods=['GET'])
@login_required
def minion_page(minion_id):
    """
    Renders the template for an advanced view of a minion

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced minion data
    """
    minion_data = salt_conn.get_specified_minion(minion_id)
    return render_template(
        'salt/advanced_minion.html',
        minion_id = str(minion_id),
        minion_data = minion_data
    )


@bp.route('/api/minion_data')
@login_required
def minion_data():
    """
    Retrieve and return the minion data

    Args: none

    Returns:
        dict: A dictionary containing the graph data with the following keys:
            - x (list): list of all minion types
            - y (lsit): number of minions for each type
    """
    data = salt_conn.get_minion_count()
    return jsonify(data)


@bp.route('/api/temp_data')
@login_required
def temp_data():
    """
    Retrieve and return the minion data

    Args: none

    Returns:
        dict: A dictionary containing the temperature data with the following keys:
            - x (list): list of all physical minions
            - y (lsit): cpu temperature for corresponding physical minion
    """
    data = {}
    nodes = salt_conn.get_physical_nodes()
    # nodes are the list of all physical nodes
    # loop through nodes and call get_cpu_temp on each minion id
    print (nodes)
    for node in nodes:
        data[node] = salt_conn.get_cpu_temp(node)
    return jsonify(data)


@bp.route('/physical', methods=['GET'])
@login_required
def physical():
    """
    Renders the active jobs from the server.

    Returns:
        str: The rendered HTML template for displaying the active jobs.
    """
    hostname = salt_call.salt_conn()['hostname']
    json_data = salt_conn.get_all_jobs()
    if json_data == False:
      return render_template('salt/salt_error.html')
    return render_template(
        'salt/physical.html',
        hostname = hostname, 
        json_data = json_data
    )