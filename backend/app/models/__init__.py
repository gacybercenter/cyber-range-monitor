from .datasource import Guacamole, Openstack, Saltstack
from .enums import Role
from .logs import EventLog
from .user import User

model_map = {
    'user': User,
    'guac': Guacamole,
    'openstack': Openstack,
    'saltstack': Saltstack,
    'logs': EventLog,
}
