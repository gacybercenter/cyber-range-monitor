"""
Saltstack plugin for Range Monitor.
"""
import datetime
import json
from flask import Blueprint, render_template, jsonify, request
from range_monitor.auth import login_required, admin_required, user_required
from . import salt_call

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
    data_source = salt_call.salt_conn()
    args = ['id', 'osfinger', 'uuid', 'build_phase', 'role', 'fqdn_ip4', 'username']

    json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_minions_args", args)
    minion_data = json_data['return'][0]['salt-dev']
    print(minion_data)
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
    data_source = salt_call.salt_conn()
    json_data = salt_call.execute_function(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_jobs")
    print(json_data)
    return render_template('salt/jobs.html', json_data = json_data)


@bp.route('/minions/<string:minion_id>', methods=['GET'])
@login_required
def minion_page(minion_id):
    """
    Renders the template for an advanced view of a minion

    Accepts: minion_id: which minion to get information for 

    Returns: rendered HTML template for displaying advanced minion data
    """

    # x_info is an array used to pass commands to salt => [tgt, cmd]
    uptime_info = [minion_id, 'status.uptime']
    load_info = [minion_id, 'status.loadavg']

    # running commands passed into x_array using salt_call
    data_source = salt_call.salt_conn()
    uptime_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.targeted_command", uptime_info)
    load_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.targeted_command", load_info)

    # creating minion_data nested dictionary with all necesary data
    minion_data = {}
    for data_item in uptime_data['return']:
        for master_id, master_data in data_item.items():
            if minion_id in master_data:
                uptime = master_data[minion_id]
                for load_item in load_data['return']:
                    if minion_id in load_item.get(master_id, {}):
                        load = load_item[master_id][minion_id]
                        minion_data[minion_id] = {'uptime_data': uptime, 'load_data': load}
    print(minion_data)
    
    # render html, minion_id and minion_data passed into html template
    return render_template('salt/advanced_minion.html', minion_id = str(minion_id), minion_data = minion_data)