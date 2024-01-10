"""
Connects to Guacamole using the configuration specified in the 'config.yaml' file.
"""

from yaml import safe_load
from range_monitor.db import get_db
from guacamole import session


def read_config():
    """
    Reads the 'config.yaml' file and returns the loaded configuration.

    Returns:
        The loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the 'config.yaml' file is not found.
    """
    try:
        with open('clouds.yaml', 'r', encoding='utf-8') as config_file:
            config = safe_load(config_file)
    except FileNotFoundError:
        return None

    return config


def guac_connect(identifier=1):
    """
    Connects to Guacamole using the configuration specified in the 'config.yaml' file.

    Returns:
        gconn (guac_connection): The connection object to Guacamole.
    """
    db = get_db()
    guac_entry = db.execute(
        'SELECT p.*'
        ' FROM guacamole p'
        ' WHERE p.id = ?', (identifier,)
    ).fetchone()

    guac_config = {
        key: guac_entry[key]
        for key in guac_entry.keys()
    }

    print(guac_config)

    gconn = session(guac_config['endpoint'],
                    guac_config['datasource'],
                    guac_config['username'],
                    guac_config['password'])

    return gconn
