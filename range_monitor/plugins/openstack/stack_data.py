"""
Gets data from OpenStack
"""

from datetime import datetime
from openstack import connection
from . import stack_conn # Import the connection setup from stack_conn.py

def get_active_conns():
    """
     Retrieves a list of active connections in an OpenStack environment.

    Returns:
        dict: A dictionary containing active connections grouped by project.
            Each key represents a project name, and its corresponding value is a
            list of dictionaries, each containing the instance name and the
            username associated with that instance.
    """
    try:
        gconn = stack_conn.openstack_connect()

        active_data = []
        for instance in gconn.compute.servers(details=True):  # Removed all_projects=True
            if instance.status == 'ACTIVE':
                project = gconn.identity.get_project(instance.project_id)
                active_data.append({
                    'instance': instance.name,
                    'project': project.name
                })
        return active_data
    except Exception as e:
        print(f"Error fetching active connections: {e}")
        return []

def get_active_instances():
    """
    Retrieves a list of active connections.

    Returns:
        list: A list of dictionaries, each representing an active instance.
    """

    conn = stack_conn.openstack_connect()

    active_instances = [instance.to_dict() for instance in conn.compute.servers(details=True, status="ACTIVE")]

    return active_instances

def get_projects_data():
    """
    Retrieves a list of projects (tenants) in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a project
    """

    conn = stack_conn.openstack_connect()

    projects = [project.to_dict() for project in conn.identity.projects()]

    return projects

def get_instance_history(instance_id): # TODO: implement this accordingly on monitoring setup
    """
    Retrieves the activity history of a specific instance from OpenStack's telemetry service.

    Parameters:
        instance_id (str): The ID of the instance to retrieve the history for.
        
    Returns:
        list: A list of events related to the instance.
    """
    conn = stack_conn.openstack_connect()

    # directly calling Ceilometer or an equivalent service
    #    and that it's configured to collect relevant instance events/metrics.
    try:
        events = conn.telemetry.list_events(q=[{"field": "resource_id", "op": "eq", "value": instance_id}])
    except AttributeError:
        print("Telemetry service is not configured properly.")
        return []
    
    history = []

    for event in events:
        event_details = {
            'event_type':event.event_type,
            'timestamp':event.generated,
            'detail':event.traits
        }
        history.append(event_details)

    return history

def get_networks_data():
    """
    Retrieves a list of networks in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a network.
    """

    conn = stack_conn.openstack_connect()

    networks = [network.to_dict() for network in conn.network.networks()]

    return networks

def get_volumes_data():
    """
    Retrieves a list of volumes in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a volume.
    """

    conn = stack_conn.openstack_connect()

    volumes = [volume.to_dict() for volume in conn.block_storage.volumes(details=True)]

    return volumes

def get_network_details(network_id):
    """
    Retrieves a list of networks in OpenStack.

    Returns: 
        list: A list of dictionaries, each representing a network.
    """

    conn = stack_conn.openstack_connect()
    networks = conn.network.get_network(network_id)

    return network.to_dict()

def get_volume_details():
    """
    Retrieves a list of volumes in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a volume.
    """

    conn = stack_conn.openstack_connect()
    volumes = conn.block_storage.get_volume(volume_id)

    return volume.to_dict()

def get_performance_data()
    """
    Retrieves a list of performances in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a performance.
    """
    response = requests.get('http://example.com/api/performance_data')
    response.raise_for_status()  # Check if the request was successful
    return response.json()
