"""
Saltstack plugin for Range Monitor.
"""
import datetime
import json
from flask import Blueprint, render_template, jsonify, request
from range_monitor.auth import login_required, admin_required, user_required
from . import salt_call
from . import salt_conn

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
    minion_data = salt_conn.get_all_minions()
    return render_template('salt/minions.html', json_data=minion_data)

# @bp.route('/minions', methods=['GET'])
# @login_required
# def minions():
#     """
#     Renders the active minions from the server.

#     Returns:
#         str: HTML template for rendering minions and the minion data
#     """
#     data_source = salt_call.salt_conn()
#     args = ['id', 'osfinger', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']

#     json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_minions_args", args)
#     minion_data = json_data['return'][0]['salt-dev']
#     print(minion_data)
#     return render_template('salt/minions.html', json_data=minion_data)

@bp.route('/events', methods=['GET'])
@login_required
def events():
    """
    Renders the events from the server.

    Returns:
        str: The rendered HTML template for displaying the events.
    """
    return render_template('salt/events.html')


@bp.route('/jobs', methods=['GET'])
@login_required
def jobs():
    """
    Renders the active jobs from the server.

    Returns:
        str: The rendered HTML template for displaying the active jobs.
    """
    json_data = salt_conn.get_all_jobs()
    print(json_data)
    sorted_data = sorted(json_data["return"][0].items(), key=lambda x: x[1]["target"])
    print(sorted_data)
    return render_template('salt/jobs.html', json_data = sorted_data)


@bp.route('/jobs/<string:job_id>', methods=['GET'])
@login_required
def job_page(job_id):
    """
    Renders the template for an advanced view of a minion

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced minion data
    """

    job_json = salt_conn.get_specified_job(job_id)
    
    # render html, minion_id and minion_data passed into html template
    return render_template('salt/advanced_job.html', job_id = str(job_id), job_data = job_json)


@bp.route('/minions/<string:minion_id>', methods=['GET'])
@login_required
def minion_page(minion_id):
    """
    Renders the template for an advanced view of a minion

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced minion data
    """

    minion_data = salt_conn.get_specified_minion(minion_id)

    print(minion_data)

    # render html, minion_id and minion_data passed into html template
    return render_template(
        'salt/advanced_minion.html',
        minion_id = str(minion_id),
        minion_data = minion_data
    )