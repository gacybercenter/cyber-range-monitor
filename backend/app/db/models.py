from app.api.users.model import User, Role
# from app.api.event_logs.model import EventLog, EventLogLevel

from app.api.datasources.open_stack.model import OpenstackSource
from app.api.datasources.salt_stack.model import SaltstackSource
from app.api.datasources.guac.model import GuacamoleSource


# without doing this, the base database model has no knowledge of the other tables

MODEL_LIST = [
    User,
    OpenstackSource,
    SaltstackSource,
    GuacamoleSource,
    # EventLog
]


__all__ = [
    'User',
    'GuacamoleSource',
    'OpenstackSource',
    'SaltstackSource',
    # 'EventLog',
    # 'EventLogLevel',
    'Role'
]
