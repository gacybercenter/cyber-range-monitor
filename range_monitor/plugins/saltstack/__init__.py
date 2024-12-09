"""
Saltstack plugin for Range Monitor.
"""
from flask import Blueprint, render_template, jsonify
from range_monitor.auth import login_required
from . import salt_call
from . import salt_conn

bp = Blueprint('salt',
                __name__,
                template_folder='./templates',
                static_folder='./static')

salt_cache = {
    'hostname': None
}

@bp.route('/')
@login_required
def home():
    """
    Renders the active minions from the server.

    Returns:
    str: The rendered HTML template for displaying the active minions.
    """
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    minion_data = salt_conn.get_all_minions()
    if minion_data == False:
        return render_template('salt/salt_error.html')
    return render_template(
        'salt/minions.html',
        hostname = salt_cache['hostname'],
        json_data=minion_data,
    )


@bp.route('/minion_graph', methods=['GET'])
@login_required
def minion_graph():
    """
    Renders the events from the server.

    Returns:
        str: The rendered HTML template for displaying accepted minions.
    """
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    return render_template(
        'salt/minion_graph.html', 
        hostname = salt_cache['hostname'])


@bp.route('/jobs', methods=['GET'])
@login_required
def jobs():
    """
    Renders the active jobs from the server.

    Returns:
        str: The rendered HTML template for displaying recent jobs
    """
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    json_data = salt_conn.get_all_jobs()
    if json_data == False:
      return render_template('salt/salt_error.html')
    return render_template(
        'salt/jobs.html',
        hostname = salt_cache['hostname'], 
        json_data = json_data
    )


@bp.route('/jobs/<string:job_id>', methods=['GET'])
@login_required
def job_page(job_id):
    """
    Renders the template for an advanced view of a job

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced job data
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


@bp.route('/api/cpu_temp')
@login_required
def api_cpu():
    """
    Retrieve and return the pysical node temperature data

    Args: none

    Returns:
        dict: A dictionary containing the temperature data in this format:
            { minion_id: cpu_temperature}
    """
    data = {}
    nodes = salt_conn.get_physical_nodes()
    # nodes are the list of all physical nodes
    # loop through nodes and call get_cpu_temp on each minion id
    for node in nodes:
      temperature = salt_conn.get_cpu_temp(node)
      if temperature == None:
        continue
      data[node] = temperature
    return jsonify(data)


@bp.route('/api/system_temp')
@login_required
def api_system():
    """
    Retrieve and return the physical node temperature data

    Args: none

    Returns:
        dict: A dictionary containing the temperature data in this format:
            { minion_id: system_temperature}
    """
    data = {}
    nodes = salt_conn.get_physical_nodes()
    # nodes are the list of all physical nodes
    # loop through nodes and call get_system_temp on each minion id
    for node in nodes:
      temperature = salt_conn.get_system_temp(node)
      if temperature == None:
        continue
      data[node] = temperature
    return jsonify(data)

@bp.route('/cpu_temp', methods=['GET'])
@login_required
def cpu_temp():
    """
    CPU temperature trends route

    Returns:
        str: The rendered HTML template for displaying a line graph of the cpu temperature trends.
    """
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    return render_template(
        'salt/cpu_temp.html', 
        hostname = salt_cache['hostname'])

@bp.route('/system_temp', methods=['GET'])
@login_required
def system_temp():
    """
    System temperature trends route

    Returns:
        str: The rendered HTML template for displaying a line graph of the system temperature trends.
    """
    if salt_cache['hostname'] == None:
      data_source = salt_call.salt_conn()
      salt_cache['hostname'] = data_source['hostname']
    return render_template(
        'salt/system_temp.html', 
        hostname = salt_cache['hostname'])