"""
Connects to OpenStack using the configuration specified in the 'clouds.yaml' 
file or from the database if no cloud is provided.
"""

import openstack
from typing import Optional, Union
from functools import cache
import range_monitor.db as sqlite3_wrapper
import logging

logging.basicConfig(level=logging.INFO)


@cache
def connect(cloud: Optional[str] = None) -> Optional[
    openstack.connection.Connection]:
    """
    Connects to OpenStack. If a cloud is provided, connects using the 
    'clouds.yaml' configuration. Otherwise, retrieves OpenStack connection 
    details from the database.

    :param cloud: Optional name of the cloud in 'clouds.yaml' to connect to.
    :return: OpenStack Connection object if successful, None otherwise.
    """
    if cloud:
        logging.info(
            f"Connecting to OpenStack using cloud: {cloud}"
        )
        return openstack.connect(cloud=cloud)

    logging.info(
        "No cloud provided. Retrieving OpenStack config from the database..."
    )
    database = sqlite3_wrapper.get_db()

    try:
        openstack_entry = database.execute(
            "SELECT * FROM openstack WHERE enabled = 1"
        ).fetchone()
    except Exception as e:
        logging.error(
            f"Failed to retrieve OpenStack entry from the database: {e}"
        )
        return None

    if not openstack_entry:
        logging.warning("No enabled OpenStack entry found in the database.")
        return None

    openstack_config = dict(openstack_entry)
    logging.info(
        f"Connecting to OpenStack with config: {openstack_config['auth_url']}"
    )

    try:
        return openstack.connect(
            auth_url=openstack_config["auth_url"],
            project_id=openstack_config["project_id"],
            project_name=openstack_config["project_name"],
            username=openstack_config["username"],
            password=openstack_config["password"],
            user_domain_name=openstack_config["user_domain_name"],
            project_domain_name=openstack_config["project_domain_name"],
            region_name=openstack_config["region_name"],
            identity_api_version=openstack_config["identity_api_version"]
        )
    except Exception as e:
        logging.error(f"Failed to connect to OpenStack: {e}")
        return None
