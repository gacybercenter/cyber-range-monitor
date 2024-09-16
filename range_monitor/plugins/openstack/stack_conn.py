"""
Connects to OpenStack using the configuration specified in the 'clouds.yaml' file.
"""

import openstack
from range_monitor.db import get_db 
from openstack.connection import Connection
from typing import Dict

def openstack_connect():
    """
    Connects to OpenStack using the configurations for the specified in the 'config.yaml' file and database entries.
 
    Return:
        conn (openstack.connection.Connection): The connection object to OpenStack.
    """
    db = get_db()
    openstack_entry = db.execute(
        'SELECT p.*'
        ' FROM openstack p'
        ' WHERE p.enabled = 1'
    ).fetchone()

    if not openstack_entry:
        return None

    openstack_config: Dict[str, str] = dict(openstack_entry)
    # openstack_config = {
    #     key: openstack_entry[key]
    #     for key in openstack_entry.keys()
    # }

    conn = Connection(
        auth_url=openstack_config['auth_url'],
        project_id=openstack_config['project_id'],
        project_name=openstack_config['project_name'],
        username=openstack_config['username'],
        password=openstack_config['password'],
        user_domain_name=openstack_config.get('user_domain_name', 'Default'),
        project_domain_name=openstack_config.get('project_domain_name', 'Default'),
        region_name=openstack_config.get('region_name', 'RegionOne'),
        identity_api_version=openstack_config['identity_api_version']
    )
    
    conn = openstack.connect(cloud="gcr")
    return conn
