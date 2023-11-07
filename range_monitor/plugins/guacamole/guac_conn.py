"""
Connects to Guacamole using the configuration specified in the 'config.yaml' file.
"""

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
    except FileNotFoundError as error:
        raise FileNotFoundError('clouds.yaml file not found') from error

    return config


def guac_connect():
    """
    Connects to Guacamole using the configuration specified in the 'config.yaml' file.

    Returns:
        gconn (guac_connection): The connection object to Guacamole.
    """

    config = read_config()
    guac_config = config['clouds']['guacamole']

    gconn = session(guac_config['host'],
                    guac_config['data_source'],
                    guac_config['username'],
                    guac_config['password'])

    return gconn
