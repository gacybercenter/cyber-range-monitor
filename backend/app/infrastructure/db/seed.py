from typing import Any

from app.core.security.crypto import CryptoUtils

from ._mapped_models import (
    GuacamoleSource,
    OpenstackSource,
    Role,
    SaltstackSource,
    User,
)

USER_SEED = [
    User(username="admin", password_hash=CryptoUtils.hash("admin"), role=Role.ADMIN),
    User(username="user", password_hash=CryptoUtils.hash("user"), role=Role.USER),
    User(
        username="guest", password_hash=CryptoUtils.hash("guest"), role=Role.READ_ONLY
    ),
]

GUACAMOLE_SEED = [
    GuacamoleSource(
        username="Admninistrator",
        password=CryptoUtils.encrypt("password"),
        endpoint="localhost",
        datasource="mysql",
        enabled=True,
    )
]


OPENSTACK_SEED = [
    OpenstackSource(
        endpoint="http://localhost:5000/v3",
        project_id="projectID",
        project_name="service",
        username="neutron",
        password=CryptoUtils.encrypt("password"),
        user_domain_name="Default",
        project_domain_name="Default",
        region_name="RegionOne",
        identity_api_version="3",
        enabled=True,
    )
]

SALTSTACK_SEED = [
    SaltstackSource(
        endpoint="http://localhost:8080/salt/",
        username="Administrator",
        password=CryptoUtils.encrypt("Administrator"),
        hostname="hostname",
        enabled=True,
    )
]

# EVENT_LOG_SEED = [
#     EventLog(
#         log_level=EventLogLevel.INFO,
#         message="This is an info level log."
#     ),
#     EventLog(
#         log_level=EventLogLevel.WARNING,
#         message="This is a warning level log."
#     ),
#     EventLog(
#         log_level=EventLogLevel.ERROR,
#         message="This is an error level log."
#     ),
#     EventLog(
#         log_level=EventLogLevel.CRITICAL,
#         message="This is a critical level log."
#     ),
# ]


def get_seed_data() -> list[Any]:
    """returns a list of all the seed data to be inserted into the database"""
    return [
        USER_SEED,
        GUACAMOLE_SEED,
        OPENSTACK_SEED,
        SALTSTACK_SEED,
    ]
