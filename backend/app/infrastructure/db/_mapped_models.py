from app.api.domains.datasource.models import (
    GuacamoleDataSource,
    OpenStackDataSource,
    SaltStackDataSource,
)
from app.api.domains.users.model import User

# without doing this, the base database model has no knowledge of the other tables

MODEL_LIST = [
    User,
    SaltStackDataSource,
    OpenStackDataSource,
    GuacamoleDataSource,
    # EventLog
]


__all__ = [
    'User',
    'SaltStackDataSource',
    'OpenStackDataSource',
    'GuacamoleDataSource',
]
