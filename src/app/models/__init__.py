from ..auth.user import User
from .datasource import Guacamole, Openstack, Saltstack
from ..logging.log_model import EventLog
from .enums import Role

model_map = {
    'user': User,
    'guac': Guacamole,
    'openstack': Openstack,
    'saltstack': Saltstack,
    'logs': EventLog,
}
