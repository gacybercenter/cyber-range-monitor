import flask
import openstack
import json
from range_monitor.auth import login_required, admin_required, user_required
from .stack_class import StackConnection
from . import stack_data
from . import stack_conn
from . import parse
import time
import logging


class OpenStackBlueprint:
    def __init__(self, import_name, template_folder, static_folder):
        self.blueprint = flask.Blueprint(
            import_name,
            __name__,
            template_folder=template_folder,
            static_folder=static_folder
        )
        self._connection = None
        self.register_routes()
        
    @property
    def connection(self):
        if self._connection is None:
            self._connection = StackConnection()
        
        return self._connection
    
    def register_routes(self):
        @self.blueprint.route("/")
        @login_required
        def dashboard() -> str:
            """
            Renders a general dashboard.

            Returns:
                str: The rendered HTML template for the dashboard.
            """
            
            instances_summary = {
                "active_instances": sum(
                    1 for server in self.connection.servers if server.status == "ACTIVE"
                ),
                "total_instances": len(self.connection.servers)
            }
            
            networks_summary = {
                "active_networks": sum(
                    1 for network in self.connection.networks if network.status == "ACTIVE"
                ),
                "total_networks": len(self.connection.networks)
            }
            
            data = {
                "instances_summary": instances_summary,
                "networks_summary": networks_summary
            }
            
            return flask.render_template("pages/dashboard.html", data=data)
            # return flask.render_template("openstack_base.html")
        
        @self.blueprint.route("/systems_health/")
        @login_required
        def systems_health():
            servers_summary = {
                "active_servers": sum(
                    1 for server in self.connection.servers if server.status == "ACTIVE"
                ),
                "total_servers": len(self.connection.servers)
            }
            
            networks_summary = {
                "active_networks": sum(
                    1 for network in self.connection.networks if network.status == "ACTIVE"
                ),
                "total_networks": len(self.connection.networks)
            }
            
            data = {
                "servers_summary": servers_summary,
                "networks_summary": networks_summary
            }
            
            return flask.render_template("openstack/systems_health.html", data=data)
        
        @self.blueprint.route("/topology/", methods=["GET"])
        @login_required
        def topology() -> str:
            """
            Renders the OpenStack topology.

            Returns:
                str: The rendered HTML template for the topology page.
            """
            return flask.render_template("openstack/topology.html")
        
        @self.blueprint.route("/performance/")
        @login_required
        def performance():
            cpu_usage_data = []
            memory_usage_data = []
            for server in self.connection.servers:
                if server.status != "ACTIVE":
                    continue
                
                diagnostics = self.connection.connection.compute.get_server_diagnostics(server.id)
                cpu_stats = diagnostics.get("cpu_details", [])
                memory_stats = diagnostics.get("memory_details", [])
                
                total_cpu = sum([cpu["time"] for cpu in cpu_stats if "time" in cpu])
                total_memory = sum([memory["usage"] for memory in memory_stats if "usage" in memory])
                
                cpu_usage_data.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "cpu_usage": total_cpu
                })
                memory_usage_data.append({
                    "server_id": server.id,
                    "server_name": server.name,
                    "memory_usage": total_memory
                })
            
            performance_data = {
                "cpu_usage": cpu_usage_data,
                "memory_usage": memory_usage_data
            }
            print(f"\n\n\n\n{performance_data["cpu_usage"][0]["server_id"]}n\n\n\n")
            return flask.render_template("openstack/performance.html", data=performance_data)
        
        @self.blueprint.route("/api/overview_data/", methods=["GET"])
        @login_required
        def api_overview_data() -> flask.jsonify:
            """
            API endpoint to provide updated overview data.

            Returns:
                flask.jsonify: JSON response containing instance and network summaries.
            """
            
            instances_summary = {
                "active_instances": sum(
                    1 for server in self.connection.servers if server.status == "ACTIVE"
                ),
                "total_instances": len(self.connection.servers)
            }
            
            networks_summary = {
                "active_networks": sum(
                    1 for network in self.connection.networks if network.status == "ACTIVE"
                ),
                "total_networks": len(self.connection.networks)
            }
            
            data = {
                "instances_summary": instances_summary,
                "networks_summary": networks_summary
            }
            return flask.jsonify(data)
        
        
            
