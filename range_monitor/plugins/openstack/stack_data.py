"""
Gets data from OpenStack
"""
import logging
from datetime import datetime
from openstack import connection
from . import stack_conn  # Import the connection setup from stack_conn.py

def get_active_conns():
    """
    Retrieves a list of active connections in an OpenStack environment.

    Returns:
        dict: A dictionary containing active connections grouped by project.
            Each key represents a project name, and its corresponding value is a
            list of dictionaries, each containing the instance name and the
            username associated with that instance.
    """
    conn = stack_conn.openstack_connect()
    if conn is None:
        print("Failed to establish OpenStack connection.")
        return []

    active_data = []
    for instance in conn.compute.servers(details=True):
        if instance.status == 'ACTIVE':
            project = conn.identity.get_project(instance.project_id)
            active_data.append({
                'instance': instance.name,
                'project': project.name
            })
    print("Active Connections Data:", active_data)
    return active_data

def get_active_connections():
    """
    Retrieves a list of active connections.

    Returns:
        list: A list of dictionaries, each representing an active connection with its ID and name.
    """
    conn = stack_conn.openstack_connect()
    active_connections = []
    for instance in conn.compute.servers(details=True, status="ACTIVE"):
        active_connections.append({
            'id': instance.id,
            'instance': instance.name
        })
    return active_connections
def get_active_networks():
    """
    Retrieves a list of active networks.

    Returns:
        list: A list of dictionaries, each representing an active network.
    """
    conn = stack_conn.openstack_connect()
    networks = conn.network.networks()
    active_network_count = sum(1 for network in networks if network.status == 'ACTIVE')
    return active_network_count
    
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

def get_instance_history(instance_id):
    """
    Retrieves the activity history of a specific instance from OpenStack's telemetry service.

    Parameters:
        instance_id (str): The ID of the instance to retrieve the history for.
        
    Returns:
        list: A list of events related to the instance.
    """
    conn = stack_conn.openstack_connect()

    try:
        events = conn.telemetry.list_events(q=[{"field": "resource_id", "op": "eq", "value": instance_id}])
    except AttributeError:
        print("Telemetry service is not configured properly.")
        return []
    
    history = []

    for event in events:
        event_details = {
            'event_type': event.event_type,
            'timestamp': event.generated,
            'detail': event.traits
        }
        history.append(event_details)

    return history

def get_connection_history(conn_identifier):
    """
    Returns the connection history for a given connection identifier.

    Parameters:
        conn_identifier (str): The identifier of the connection to fetch the history for.
    
    Returns:
        list: A list of dictionaries containing connection history.
    """
    conn = stack_conn.openstack_connect()

    if not conn_identifier:
        return []

    try:
        # Attempt to get the telemetry service endpoint
        if 'metering' in conn.session.get_services():
            events = conn.telemetry.list_events(q=[{"field": "resource_id", "op": "eq", "value": conn_identifier}])
        else:
            raise Exception("Telemetry service endpoint not found.")
        
        history = []
        for event in events:
            event_details = {
                'event_type': event.event_type,
                'timestamp': event.generated,
                'detail': event.traits
            }
            history.append(event_details)

        return history
    except Exception as e:
        logging.error(f"Error fetching connection history: {e}")
        return []
        
def get_networks_data():
    """
    Retrieves a list of networks in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a network.
    """

    conn = stack_conn.openstack_connect()

    networks = [network.to_dict() for network in conn.network.networks()]

    return networks

def get_network_details(network_id):
    """
    Retrieves details of a specific network in OpenStack.

    Parameters:
        network_id (str): The ID of the network to retrieve details for.

    Returns: 
        dict: A dictionary representing the network details.
    """

    conn = stack_conn.openstack_connect()
    network = conn.network.get_network(network_id)

    return network.to_dict()

def get_volume_details(volume_id):
    """
    Retrieves details of a specific volume in OpenStack.

    Parameters:
        volume_id (str): The ID of the volume to retrieve details for.

    Returns:
        dict: A dictionary representing the volume details.
    """

    conn = stack_conn.openstack_connect()
    volume = conn.block_storage.get_volume(volume_id)

    return volume.to_dict()

def get_performance_data():
    """
    Retrieves performance data from an external API.

    Returns:
        list: A list of dictionaries, each representing a performance.
    """
    response = requests.get('http://example.com/api/performance_data')
    response.raise_for_status()  # Check if the request was successful
    return response.json()
#========================================+
def get_topology_data():
    """
    Retrieves topology data from OpenStack.

    Returns:
        dict: A dictionary containing topology data.
    """
    try:
        conn = stack_conn.openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return {}

        # Replace with your actual logic to get topology data
        nodes = []
        for server in conn.compute.servers(details=True):
            node = {
                "identifier": server.id,
                "name": server.name,
                "type": "server",
                "activeConnections": len(server.addresses),
                "protocol": server.status,
                "size": 1.5
            }
            nodes.append(node)

        topology_data = {
            "nodes": nodes,
            "links": []  # Add logic to generate links if needed
        }

        logging.debug(f"Topology Data: {topology_data}")
        return topology_data
    except Exception as e:
        logging.error(f"Error fetching topology data: {e}")
        return {}

############

def get_cpu_usage():
    """
    Retrieve the CPU usage for each active instance.

    Returns:
        list: A list of dictionaries containing the instance and its CPU usage.
    """
    try:
        conn = stack_conn.openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return {}

        cpu_usage_data = []
        for server in conn.compute.servers(details=True):
            cpu_stats = server.get('cpu_stats', {})
            total_cpu = sum(cpu_stats.values()) if isinstance(cpu_stats, dict) else 0
            cpu_usage_data.append({
                'instance': server.name,
                'cpu_usage': total_cpu
            })

        logging.debug(f"CPU Usage Data: {cpu_usage_data}")
        return cpu_usage_data
    except Exception as e:
        logging.error(f"Error fetching CPU usage data: {e}")
        return []

def get_memory_usage():
    """
    Retrieve the memory usage for each active instance.

    Returns:
        list: A list of dictionaries containing the instance and its memory usage.
    """
    try:
        conn = stack_conn.openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return {}

        memory_usage_data = []
        for server in conn.compute.servers(details=True):
            memory_stats = server.get('memory_stats', {})
            total_memory = sum(memory_stats.values()) if isinstance(memory_stats, dict) else 0
            memory_usage_data.append({
                'instance': server.name,
                'memory_usage': total_memory
            })

        logging.debug(f"Memory Usage Data: {memory_usage_data}")
        return memory_usage_data
    except Exception as e:
        logging.error(f"Error fetching memory usage data: {e}")
        return []

################
def get_projects_data():
    """
    Retrieves a list of projects in OpenStack.

    Returns:
        list: A list of dictionaries, each representing a project.
    """
    conn = stack_conn.openstack_connect()
    projects = [project.to_dict() for project in conn.identity.projects()]
    return projects

def get_disk_usage():
    """
    Retrieves disk usage data.

    Returns:
        float: The total disk usage.
    """
    # Replace with actual logic to fetch disk usage data
    return 750.2

def get_network_traffic():
    """
    Retrieves network traffic data.

    Returns:
        float: The total network traffic in MB.
    """
    # Replace with actual logic to fetch network traffic data
    return 1024.5

def get_recent_instances():
    """
    Retrieves a list of recently created instances.

    Returns:
        list: A list of dictionaries, each representing an instance.
    """
    conn = stack_conn.openstack_connect()
    instances = conn.compute.servers(details=True)
    recent_instances = sorted(instances, key=lambda x: x.created_at, reverse=True)[:10]
    return [instance.to_dict() for instance in recent_instances]

def get_top_active_users():
    """
    Retrieves a list of top active users based on resource usage.

    Returns:
        list: A list of dictionaries, each representing a user.
    """
    # Replace with actual logic to fetch top active users
    return [
        {"username": "user1", "active_connections": 5, "resource_usage": "High"},
        {"username": "user2", "active_connections": 3, "resource_usage": "Medium"},
        {"username": "user3", "active_connections": 2, "resource_usage": "Low"}
    ]

def get_cpu_usage_times():
    """
    Retrieves times for CPU usage data points.

    Returns:
        list: A list of timestamps.
    """
    # Replace with actual logic to fetch CPU usage times
    return ["2024-06-10T00:00:00Z", "2024-06-10T01:00:00Z", "2024-06-10T02:00:00Z"]

def get_cpu_usage_values():
    """
    Retrieves values for CPU usage data points.

    Returns:
        list: A list of CPU usage values.
    """
    # Replace with actual logic to fetch CPU usage values
    return [20.5, 35.2, 42.5]

def get_memory_usage_times():
    """
    Retrieves times for memory usage data points.

    Returns:
        list: A list of timestamps.
    """
    # Replace with actual logic to fetch memory usage times
    return ["2024-06-10T00:00:00Z", "2024-06-10T01:00:00Z", "2024-06-10T02:00:00Z"]

def get_memory_usage_values():
    """
    Retrieves values for memory usage data points.

    Returns:
        list: A list of memory usage values.
    """
    # Replace with actual logic to fetch memory usage values
    return [50.5, 60.2, 68.3]

def get_network_traffic_times():
    """
    Retrieves times for network traffic data points.

    Returns:
        list: A list of timestamps.
    """
    # Replace with actual logic to fetch network traffic times
    return ["2024-06-10T00:00:00Z", "2024-06-10T01:00:00Z", "2024-06-10T02:00:00Z"]

def get_network_traffic_values():
    """
    Retrieves values for network traffic data points.

    Returns:
        list: A list of network traffic values in MB.
    """
    # Replace with actual logic to fetch network traffic values
    return [300.5, 500.2, 1024.5]
