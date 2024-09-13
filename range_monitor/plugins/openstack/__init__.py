"""
OpenStack Monitor
"""

from .openstack_blueprint import OpenStackBlueprint

bp = OpenStackBlueprint("openstack", "./templates", "./static").blueprint


'''
def get_connection(cloud: Optional[str] = None):
    if "connection" not in g:
        # Initialize connection once per request
        g.connection = stack_class.StackConnection(cloud)
    return g.connection


@bp.route("/")
@login_required
def overview() -> str:
    """
    Renders a general dashboard overview.

    Returns:
        str: The rendered HTML template for the dashboard overview.
    """
    
    connection = get_connection("gcr")

    instances_summary = {
        "active_instances": sum(
            1 for server in connection.servers if server.status == "ACTIVE"
        ),
        "total_instances": len(connection.servers)
    }
    
    networks_summary = {
        "active_networks": sum(
            1 for network in connection.networks if network.status == "ACTIVE"
        ),
        "total_networks": len(connection.networks)
    }
    
    data = {
        "instances_summary": instances_summary,
        "networks_summary": networks_summary
    }

    return flask.render_template("openstack/overview.html", data=data)


@bp.route("/api/overview_data", methods=["GET"])
@login_required
def api_overview_data() -> flask.jsonify:
    """
    API endpoint to provide updated overview data.

    Returns:
        flask.jsonify: JSON response containing instance and network summaries.
    """
    connection=get_connection()
    instances_summary = {
        "active_instances": sum(
            1 for server in connection.servers if server.status == "ACTIVE"
        ),
        "total_instances": len(connection.servers)
    }
    
    networks_summary = {
        "active_networks": sum(
            1 for network in connection.networks if network.status == "ACTIVE"
        ),
        "total_networks": len(connection.networks)
    }
    
    data = {
        "instances_summary": instances_summary,
        "networks_summary": networks_summary
    }
    return flask.jsonify(data)

@bp.route("/topology", methods=["GET"])
@login_required
def topology() -> str:
    """
    Renders the OpenStack topology.

    Returns:
        str: The rendered HTML template for the topology page.
    """
    return flask.render_template("openstack/topology.html")

@bp.route("/api/topology_data", methods=["GET"])
@login_required
def topology_data() -> flask.jsonify:
    """
    API endpoint to retrieve topology data.

    Returns:
        flask.jsonify: JSON response containing topology data.
    """
    topology_data = stack_data.get_topology_data()
    return flask.jsonify(topology_data)

@bp.route("/active_instances", methods=["GET"])
@login_required
def active_instances() -> str:
    """
    Renders active OpenStack instances.

    Returns:
        str: The rendered HTML template for displaying active instances.
    """
    active_instances = stack_data.get_active_instances()
    return flask.render_template("openstack/active_instances.html", instances=active_instances)

@bp.route("/networks", methods=["GET"])
@login_required
def networks() -> str:
    """
    Renders OpenStack networks.

    Returns:
        str: The rendered HTML template for displaying networks.
    """
    networks = stack_data.get_networks_data()
    return flask.render_template("openstack/networks.html", networks=networks)

@bp.route("/networks/<network_id>", methods=["GET"])
@login_required
def network_details(network_id: str) -> str:
    """
    Renders the details of a specific network.

    Parameters:
        network_id (str): The ID of the network.

    Returns:
        str: The rendered HTML template for displaying the network details.
    """
    network = stack_data.get_network_details(network_id)
    return flask.render_template("openstack/network_details.html", network=network)

@bp.route("/volumes", methods=["GET"])
@login_required
def volumes() -> str:
    """
    Renders OpenStack volumes.

    Returns:
        str: The rendered HTML template for displaying the volumes.
    """
    volumes = stack_data.get_volume_details()
    return flask.render_template("openstack/volumes.html", volumes=volumes)

@bp.route("/performance", methods=["GET"])
@login_required
def performance() -> str:
    """
    Renders OpenStack performance metrics.

    Returns:
        str: The rendered HTML template for performance metrics.
    """
    cpu_usage_data = stack_data.get_cpu_usage()
    memory_usage_data = stack_data.get_memory_usage()
    performance_data = {
        "cpu_usage": cpu_usage_data,
        "memory_usage": memory_usage_data
    }

    return flask.render_template("openstack/performance.html", data=performance_data)

@bp.route("/api/performance_data", methods=["GET"])
@login_required
def api_performance_data() -> flask.jsonify:
    """
    API endpoint to provide updated performance data.

    Returns:
        flask.jsonify: JSON response containing CPU and memory usage data.
    """
    try:
        cpu_usage_data = stack_data.get_cpu_usage()
        memory_usage_data = stack_data.get_memory_usage()
        
        data = {
            "cpu_usage": cpu_usage_data,
            "memory_usage": memory_usage_data
        }
        return flask.jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching performance data: {e}")
        return flask.jsonify({"error": str(e)}), 500

@bp.route("/connections_graph", methods=["GET"])
@login_required
def connections_graph() -> str:
    """
    Renders the connections graph overview.

    Returns:
        str: The rendered HTML template for the connections graph overview.
    """
    connections_graph_data = stack_data.get_connections_graph_data()
    data = {
        "connections_graph_data": connections_graph_data
    }

    return flask.render_template("openstack/connections_graph.html", data=data)

@bp.route("/active_connections", methods=["GET"])
@login_required
def active_connections_data() -> str:
    """
    Renders active connections.

    Returns:
        str: The rendered HTML template for displaying active connections.
    """
    active_connections = stack_data.get_activity_info()
    return flask.render_template("openstack/active_connections.html", connections=active_connections)

@bp.route("/api/active_connections_data", methods=["GET"])
@login_required
def api_active_connections_data() -> flask.jsonify:
    """
    API endpoint to provide updated active connections data.

    Returns:
        flask.jsonify: JSON response containing active connection data.
    """
    try:
        active_connections = stack_data.get_activity_info()
        return flask.jsonify(active_connections)
    except Exception as e:
        logging.error(f"Error fetching active connections data: {e}")
        return flask.jsonify({"error": str(e)}), 500

@bp.route("/active_users", methods=["GET"])
@login_required
def active_users() -> str:
    """
    Renders active users.

    Returns:
        str: The rendered HTML template for displaying active users.
    """
    active_users = stack_data.get_active_users()
    return flask.render_template("openstack/active_users.html", users=active_users)

@bp.route("/timeline", methods=["GET", "POST"])
@login_required
def connection_timeline() -> str:
    """
    Renders the connection timeline page and fetches the history if a connection is selected.

    Returns:
        str: The rendered HTML template for displaying the connection timeline.
    """
    connections = stack_data.get_active_connections()
    history = None

    if flask.request.method == "POST":
        conn_identifier = flask.request.form.get("conn_identifier")
        if conn_identifier:
            history = stack_data.get_connection_history(conn_identifier)
            print("History data:", history)  # Log the history data
            history = parse.format_history(history)

    return flask.render_template("openstack/timeline.html", connections=connections, history=json.dumps(history) if history else None)

@bp.route("/select_connection", methods=["GET"])
@login_required
def select_connection() -> str:
    """
    Renders the page to select a connection to view its timeline.

    Returns:
        str: The rendered HTML template for selecting a connection.
    """
    connections = stack_data.get_active_connections()
    return flask.render_template("openstack/select_connection.html", connections=connections)

@bp.route("/connections", methods=["GET"])
@login_required
def connections_list() -> str:
    """
    Renders the page listing all active connections.

    Returns:
        str: The rendered HTML template for listing connections.
    """
    connections = stack_data.get_active_connections()
    return flask.render_template("openstack/list_connections.html", connections=connections)

@bp.route("/input_connection", methods=["GET"])
@login_required
def input_connection() -> str:
    """
    Renders the page to input a connection ID.

    Returns:
        str: The rendered HTML template for inputting a connection ID.
    """
    return flask.render_template("openstack/input_connection.html")

@bp.route("/api/active_networks", methods=["GET"])
@login_required
def api_active_networks() -> flask.jsonify:
    """
    API endpoint to provide the active networks count.

    Returns:
        flask.jsonify: JSON response containing the active networks count.
    """
    try:
        active_networks_count = stack_data.get_active_networks()
        return flask.jsonify(active_networks_count)
    except Exception as e:
        logging.error(f"Error fetching active networks count: {e}")
        return flask.jsonify({"error": str(e)}), 500

@bp.route("/api/instance_details", methods=["GET"])
@login_required
def api_instance_details() -> flask.jsonify:
    """
    API endpoint to provide details for a specific instance.

    Returns:
        flask.jsonify: JSON response containing instance details.
    """
    instance_name = flask.request.args.get("instance")
    try:
        instance_details = stack_data.get_instance_details(instance_name)
        return flask.jsonify(instance_details)
    except Exception as e:
        logging.error(f"Error fetching details for instance {instance_name}: {e}")
        return flask.jsonify({"error": str(e)}), 500
'''
