"""
Connects to OpenStack using the configuration specified in the 'clouds.yaml' file.
"""

from range_monitor.db import get_db 
from openstack import connection

def openstack_connect():
    """
    Connects to OpenStack using the configurations for the specified in the 'config.yaml' file and database entries.
 
    Return:
        conn (openstack.connection.Connection): The connection object to OpenStack.
    """
    db = get_db()
    openstack_entry = db.execute(
        'SELECT p.*'
        ' FROM openstack_config p'
        ' WHERE p.enabled = 1'
    ).fetchone()

    if not openstack_entry:
        return None

    connection_config = {
        'auth_url': openstack_entry['auth_url'],
        'project_name': openstack_entry['project_name'],
        'username': openstack_entry['username'],
        'password': openstack_entry['password'],
        'user_domain_name': openstack_entry.get('user_domain_name', 'Default'),  
        'project_domain_name': openstack_entry.get('project_domain_name', 'Default'),
        'region_name': openstack_entry.get('region_name', 'RegionOne'), 
    }

    conn = openstack.connect(**connection_config)

    return conn