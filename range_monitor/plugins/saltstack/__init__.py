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
    return render_template(
        'salt/minions.html',
        json_data=minion_data
    )

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
    return render_template(
        'salt/jobs.html', 
        json_data = 
        json_data
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
    # render html, minion_id and minion_data passed into html template
    return render_template(
        'salt/advanced_minion.html',
        minion_id = str(minion_id),
        minion_data = minion_data
    )