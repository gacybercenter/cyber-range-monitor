"""
Connects to Guacamole using the configuration specified in the 'config.yaml' file.
"""

from range_monitor.db import get_db
from yaml import safe_load
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


def guac_connect():
    """
    Connects to Guacamole using the configuration specified in the 'config.yaml' file.

    Returns:
        gconn (guac_connection): The connection object to Guacamole.
    """

    config = read_config()
    if config:
        guac_config = config['clouds']['guacamole']
    else:
        db = get_db()
        guac_config_list = db.execute(
            'SELECT p.*'
            ' FROM guacamole p'
            ' ORDER BY p.id'
        ).fetchall()

        guac_config = {
            key: entry[key]
            for entry in guac_config_list
            for key in entry.keys()
        }

    gconn = session(guac_config['endpoint'],
                    guac_config['datasource'],
                    guac_config['username'],
                    guac_config['password'])

    return gconn
