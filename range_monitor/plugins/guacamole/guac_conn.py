"""
Connects to Guacamole using the configuration specified in the 'config.yaml' file.
"""

from range_monitor.db import get_db
from guacamole import session


def guac_connect():
    """
    Connects to Guacamole using the configuration specified in the 'config.yaml' file.

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

    gconns = session(guac_config['endpoint'],
                     guac_config['datasource'],
                     guac_config['username'],
                     guac_config['password'])

    return gconns
