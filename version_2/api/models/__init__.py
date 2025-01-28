from .user import User
from .datasource import Guacamole, Openstack, Saltstack
from .logs import EventLog, LogLevel


model_map = {
    'user': User,
    'guac': Guacamole,
    'openstack': Openstack,
    'saltstack': Saltstack,
    'logs': EventLog,
}
