"""
Gets data from OpenStack
"""
import openstack
import logging
import requests
from datetime import datetime
from openstack import connection
from . import stack_conn

def get_activity_info(get_active=True):
    """
    Retrieves active connections from OpenStack.

    Returns:
        list: A list of dictionaries containing instance and project details of active connections.
    """
    conn = stack_conn.openstack_connect()
    
    if not conn:
        return []

    servers = conn.compute.servers(details=True)
    active_connections = []
    
    for server in servers:
        if (server.status == "ACTIVE") == get_active:
            active_connections.append({
                "instance": server.name,
                "project": server.project_id
            })

    return active_connections


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

def get_instances_summary():
    """
    Retrieves the summary of instances in OpenStack.

    Returns:
        dict: A dictionary containing the count of active and total instances.
    """
    conn = stack_conn.openstack_connect()
    
    if not conn:
        return {"active_instances": 0, "total_instances": 0}

    instances = list(conn.compute.servers(details=True))
    total_instances = len(instances)
    active_instances = sum(1 for instance in instances if instance.status == 'ACTIVE')

    return {
        "active_instances": active_instances,
        "total_instances": total_instances
    }

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

def get_networks_summary():
    """
    Retrieves the summary of networks in OpenStack.

    Returns:
        dict: A dictionary containing the count of active and total networks.
    """
    conn = stack_conn.openstack_connect()
    
    if not conn:
        return {"active_networks": 0, "total_networks": 0}

    networks = list(conn.network.networks())
    total_networks = len(networks)
    active_networks = sum(1 for network in networks if network.status == 'ACTIVE')

    return {
        "active_networks": active_networks,
        "total_networks": total_networks
    }

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
        conn = stack_conn.openstack_connect()
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
        conn = stack_conn.openstack_connect()
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
def get_instance_details(instance_name):
    """
    Retrieves details for a specific instance.

    Parameters:
        instance_name (str): The name of the instance.

    Returns:
        dict: A dictionary containing the instance details.
    """
    conn = stack_conn.openstack_connect()
    
    if not conn:
        return {}

    server = next((s for s in conn.compute.servers(details=True) if s.name == instance_name), None)
    
    if not server:
        return {}

    return {
        "instance_name": server.name,
        "project": server.project_id,
        "status": server.status,
        "created": server.created_at,
        "updated": server.updated_at,
    }

############

def get_cpu_usage():
    """
    Retrieves CPU usage data from OpenStack.

    Returns:
        dict: A dictionary containing CPU usage data.
    """
    try:
        conn = stack_conn.openstack_connect()
        if conn is None:
            logging.error("Failed to establish OpenStack connection.")
            return []

        cpu_usage_data = []
        for server in conn.compute.servers(details=True):
            try:
                if server.status.lower() != 'active':
                    logging.info(f"Skipping server {server.id} as it is not active.")
                    continue

                diagnostics = conn.compute.get_server_diagnostics(server.id)
                cpu_stats = diagnostics.get('cpu_details', [])
                total_cpu = sum([cpu['time'] for cpu in cpu_stats if 'time' in cpu])
                cpu_usage_data.append({
                    'server_id': server.id,
                    'server_name': server.name,
                    'cpu_usage': total_cpu
                })
            except openstack.exceptions.ConflictException as e:
                logging.error(f"Error fetching CPU usage for server {server.id}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error fetching CPU usage for server {server.id}: {e}")
        
        return cpu_usage_data
    except Exception as e:
        logging.error(f"Error fetching CPU usage data: {e}")
        return []

def get_memory_usage():
    """
    Retrieves memory usage data from OpenStack.

    Returns:
        dict: A dictionary containing memory usage data.
    """
    
    conn = stack_conn.openstack_connect()
    if conn is None:
        logging.error("Failed to establish OpenStack connection.")
        return []

    memory_usage_data = []
    for server in conn.compute.servers(details=True):
        
            if server.status.lower() != 'active':
                logging.info(f"Skipping server {server.id} as it is not active.")
                continue

            diagnostics = conn.compute.get_server_diagnostics(server.id)
            memory_stats = diagnostics.get('memory_details', [])
            total_memory = sum([memory['usage'] for memory in memory_stats if 'usage' in memory])
            memory_usage_data.append({
                'server_id': server.id,
                'server_name': server.name,
                'memory_usage': total_memory
            })
            
    return memory_usage_data