"""
Connects to Guacamole using the configuration specified in the 'config.yaml' file.
"""

from range_monitor.db import get_db
from guacamole import session
import time

gconn_cache = {
    'gconn': None,
    'guac_config': None,
    'last_connected': None
}


def guac_connect():
    """
    Connects to Guacamole using the configuration 
    specified in the 'config.yaml' file.

    Returns:
        gconn (guac_connection): The connection object to Guacamole.
    """

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

    # Check if guac_config has changed
    if gconn_cache['guac_config'] != guac_config:
        gconn_cache['gconn'] = None

    # more than 5 minutes since last connection
    if gconn_cache['last_connected'] is not None and time.time() - gconn_cache['last_connected'] > 300:
        gconn_cache['gconn'] = None

    if gconn_cache['gconn'] is None:
        gconn = session(
            guac_config['endpoint'],
            guac_config['datasource'],
            guac_config['username'],
            guac_config['password']
        )
        gconn_cache['gconn'] = gconn
        gconn_cache['guac_config'] = guac_config
        gconn_cache['last_connected'] = time.time()

    return gconn_cache['gconn']
