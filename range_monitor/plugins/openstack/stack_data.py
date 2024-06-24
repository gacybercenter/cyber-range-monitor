"""
Gets data from OpenStack
"""
import logging
import requests
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
    Retrieves performance data from OpenStack.

    Returns:
        dict: A dictionary containing performance data.
    """
    try:
        conn = openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return {}

        performance_data = []

        for server in conn.compute.servers(details=True):
            cpu_usage = server.vm_state  # This should be replaced with actual CPU usage data retrieval logic
            memory_usage = server.task_state  # This should be replaced with actual memory usage data retrieval logic

            data = {
                "instance": server.name,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            }
            performance_data.append(data)

        logging.debug(f"Performance Data: {performance_data}")
        return performance_data

    except Exception as e:
        logging.error(f"Error fetching performance data: {e}")
        return []

def get_connections_graph_data():
    """
    Retrieves connections graph data from OpenStack.

    Returns:
        dict: A dictionary containing connections graph data.
    """
    try:
        conn = openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return {}

        connections_graph_data = []

        for server in conn.compute.servers(details=True):
            active_connections = len(server.addresses)

            data = {
                "instance": server.name,
                "active_connections": active_connections
            }
            connections_graph_data.append(data)

        logging.debug(f"Connections Graph Data: {connections_graph_data}")
        return connections_graph_data

    except Exception as e:
        logging.error(f"Error fetching connections graph data: {e}")
        return []
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

