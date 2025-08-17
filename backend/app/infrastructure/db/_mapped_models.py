from app.api.datasources.guac.model import GuacamoleSource

# from app.api.event_logs.model import EventLog, EventLogLevel
from app.api.domains.datasources.open_stack.model import OpenstackSource
from app.api.domains.salt_stack.model import SaltstackSource
from app.domains.users.model import Role, User

# without doing this, the base database model has no knowledge of the other tables

MODEL_LIST = [
    User,
    OpenstackSource,
    SaltstackSource,
    GuacamoleSource,
    # EventLog
]

MODEL_MAP = {
    'user': User,
    'guacamole': GuacamoleSource,
    'openstack': OpenstackSource,
    'saltstack': SaltstackSource,
}

__all__ = [
    'User',
    'GuacamoleSource',
    'OpenstackSource',
    'SaltstackSource',
    # 'EventLog',
    # 'EventLogLevel',
    'Role',
]
