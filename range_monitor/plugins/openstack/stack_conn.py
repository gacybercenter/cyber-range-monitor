"""
Connects to OpenStack using the configuration specified in the 'clouds.yaml' file.
"""

from range_monitor.db import get_db #TODO: ??
from openstack import connection
import yaml
import os

def openstack_config(config_file='clouds.yaml'):
    """
    Loads OpenStack cloud configurations from a yaml file.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: A dictionary containing the OpenStack cloud configurations.
    """

    with open() as f:
        config = yaml.safe_load(f)

    return config.get('clouds')

def openstack_connect(cloud_name='mycloud'):
    """
    Connects to OpenStack using the configurations for the specified cloud.
    Uses OpenStack's 'Connection' class.
    
    Args:
        cloud_name (str): The name of the cloud configuration to use.

    Return:
        conn (openstack.connection.Connection): The connection object to OpenStack.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'clouds.yaml')
    configs = openstack_config(config_path)

    if cloud_name not in configs:
        raise ValueError(f"The cloud configuration '{cloud_name}' not found")

    cloud_config = config[cloud_name]

    conn = connection.Connection(
        region_name=cloud_config['region_name'],
        auth=dict(
            auth_url=cloud_config['auth']['auth_url'],
            username=cloud_config['auth']['username'],
            password=cloud_config['auth']['password'],
            project_id=cloud_config['auth']['project_id'],
            user_domain_name=cloud_config['auth']['user_domain_name']
        ),
        compute_api_version='latest'
        identity_interface='internal'    
    )

    return conn

#TODO: IMPLEMENT THE CODE BELOW 
#use databases to pull up the credentials to connect 
#if not work, save it as a cloud.yaml file (using "with open") then process it
    """

Connects to Guacamole using the configuration specified in the 'config.yaml' file.


from range_monitor.db import get_db
from guacamole import session


def guac_connect():
 
    Connects to Guacamole using the configuration specified in the 'config.yaml' file.

    Returns:
        gconn (guac_connection): The connection object to Guacamole.


    db = get_db()
    guac_entry = db.execute(
        'SELECT p.*'
        ' FROM guacamole p'
        ' WHERE p.enabled = 1'
    ).fetchone()

    if not guac_entry:
        return None

    guac_config = {
        key: guac_entry[key]
        for key in guac_entry.keys()
    }

    gconns = session(guac_config['endpoint'],
                     guac_config['datasource'],
                     guac_config['username'],
                     guac_config['password'])

    return gconns

    """