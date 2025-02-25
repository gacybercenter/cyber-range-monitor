from .user import User
from .datasource import Guacamole, Openstack, Saltstack
from .logs import EventLog
from .enums import Role

model_map = {
    'user': User,
    'guac': Guacamole,
    'openstack': Openstack,
    'saltstack': Saltstack,
    'logs': EventLog,
}
