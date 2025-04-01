from typing import Any
from app.extensions.security import crypto

from app.users.model import User, Role

from app.event_logs.model import EventLog, EventLogLevel

from app.openstack_source.model import OpenstackSource
from app.saltstack_source.model import SaltstackSource
from app.guacamole_source.model import GuacamoleSource


from .main import connect_db, get_session


def user_seed() -> list[User]:
    return [
        User(
            username="admin",
            password_hash=crypto.hash_password("admin"),
            role=Role.ADMIN
        ),
        User(
            username="user",
            password_hash=crypto.hash_password("user"),
            role=Role.USER
        ),
        User(
            username="guest",
            password_hash=crypto.hash_password("guest"),
            role=Role.READ_ONLY
        )
    ]


def guac_seed() -> GuacamoleSource:
    return GuacamoleSource(
        username="Admninistrator",
        password=crypto.encrypt_data("password"),
        endpoint="localhost",
        datasource="mysql",
        enabled=True,
    )


def openstack_seed() -> OpenstackSource:
    return OpenstackSource(
        auth_url="http://localhost:5000/v3",
        project_id="projectID",
        project_name="service",
        username="neutron",
        password=crypto.encrypt_data("password"),
        user_domain_name="Default",
        project_domain_name="Default",
        region_name="RegionOne",
        identity_api_version="3",
        enabled=True,
    )


def saltstack_seed() -> SaltstackSource:
    return SaltstackSource(
        endpoint="http://localhost:8080/salt/",
        username="Administrator",
        password=crypto.encrypt_data("Administrator"),
        hostname="hostname",
        enabled=True,
    )


def event_log_seed() -> list[EventLog]:
    return [
        EventLog(
            log_level=EventLogLevel.INFO,
            message="This is an info level log."
        ),
        EventLog(
            log_level=EventLogLevel.WARNING,
            message="This is a warning level log."
        ),
        EventLog(
            log_level=EventLogLevel.ERROR,
            message="This is an error level log."
        ),
        EventLog(
            log_level=EventLogLevel.CRITICAL,
            message="This is a critical level log."
        ),
    ]


async def insert_seed(seed_data: dict[str, list[Any]]) -> None:
    async with get_session() as db:
        for labels in seed_data.keys():
            print("Inserting seed data for", labels)
            for seeds in seed_data[labels]:
                db.add(seeds)
        await db.commit()


async def default_seed() -> None:
    seed_data = {
        "users": user_seed(),
        "guacamole": [guac_seed()],
        "openstack": [openstack_seed()],
        "saltstack": [saltstack_seed()],
        "event_logs": event_log_seed()
    }
    await insert_seed(seed_data)
