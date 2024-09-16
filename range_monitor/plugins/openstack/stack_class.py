import openstack
import range_monitor.db as sqlite3_wrapper
from  typing import Optional


class StackConnection:
    def __init__(self, cloud: Optional[str] = None):
        self._connection = None
        self.connection = self._initialize_connection(cloud)
        self.servers = list(self.connection.compute.servers())
        self.networks = list(self.connection.network.networks())
    
    @property
    def connection(self):
        if not self._connection:
            self._connection = self._initialize_connection()
        
        return self._connection
    
    @connection.setter
    def connection(self, new_connection):
        if isinstance(new_connection, openstack.connection.Connection):
            self._connection = new_connection
        else:
            raise ValueError(
                "Invalid connection type:\n"
                f"- Expected type: {openstack.connection.Connection}\n"
                f"- Received type: {type(new_connection)}"
            )
        
    def _initialize_connection(self, cloud: Optional[str] = None):
        if cloud is not None:
            try:
                return openstack.connect(cloud=cloud)
            except Exception as e:
                raise Exception(
                    f"Failed to initialize OpenStack connection from cloud: {e}"
                )        
        
        try:
            database = sqlite3_wrapper.get_db()
            openstack_entry = database.execute(
                "SELECT * FROM openstack WHERE enabled = 1"
            ).fetchone()
            
            if not openstack_entry:
                return None
            
            openstack_config = dict(openstack_entry)
            
            return openstack.connect(
                auth_url=openstack_config["auth_url"],
                project_id=openstack_config["project_id"],
                project_name=openstack_config["project_name"],
                username=openstack_config["username"],
                password=openstack_config["password"],
                user_domain_name=openstack_config.get("user_domain_name", "Default"),
                project_domain_name=openstack_config.get("project_domain_name", "Default"),
                region_name=openstack_config.get("region_name", "RegionOne"),
                identity_api_version=openstack_config["identity_api_version"]
            )
        
        except Exception as e:
            raise Exception(
                f"Failed to initialize OpenStack connection from database: {e}"
            )        
