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

    return render_template('salt/home.html')

@bp.route('/minions', methods=['GET'])
@login_required
def minions():
    """
    Renders the active minions from the server.

    Returns:
        str: HTML template for rendering minions and the minion data
    """
    data_source = salt_call.salt_conn()
    
    args = ['id', 'os', 'uuid', 'build_phase', 'role', 'type', 'username']

    json_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_minions_args", args)
    minion_data = json_data['return'][0]['salt-dev']
    print(minion_data)
    return render_template('salt/minions.html', json_data=minion_data)

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

    return render_template('salt/jobs.html')


@bp.route('/api/get_minions')
@login_required
def get_minions():
    """
    Retreives the minion data. Calls monitor.gather_minions_args, parses through and returns only args (id, os, saltversion, build_phase, role, type, username)

    Returns: JSON response containing minion data
    """
    data_source = salt_call.salt_conn()
    
    args = ['id', 'os', 'uuid', 'saltversion', 'build_phase', 'role', 'type', 'username']

    minion_data = salt_call.execute_function_args(data_source['username'], data_source['password'], data_source['endpoint'], "monitor.gather_minions_args", args)
    # minion_data = dict(minion_data)

    return jsonify(minion_data)