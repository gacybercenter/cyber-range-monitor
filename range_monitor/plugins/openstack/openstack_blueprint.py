import flask
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
        def overview() -> str:
            """
            Renders a general dashboard overview.

            Returns:
                str: The rendered HTML template for the dashboard overview.
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

            return flask.render_template("openstack/overview.html", data=data)
        
        @self.blueprint.route("/api/overview_data", methods=["GET"])
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
