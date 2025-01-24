from api.models.user import User
from api.models.data_source import Guacamole, Openstack, Saltstack
from api.models.logs import EventLog, LogLevel



model_map = {
    'user': User,
    'guac': Guacamole,
    'openstack': Openstack,
    'saltstack': Saltstack,
    'logs': EventLog,
}
