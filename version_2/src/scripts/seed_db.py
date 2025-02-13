import asyncio

from app.security import crypto_utils
from app.db import get_session, connect_db
from app.models.enums import LogLevel
from app.models import (
    Guacamole,
    Openstack,
    Saltstack,
    EventLog,
    User,
    Role
)

SEED_DATA = {
    'users': [
        User(
            username='admin',
            password_hash=crypto_utils.hash_password('admin'),
            role=Role.ADMIN
        ),
        User(
            username='user',
            password_hash=crypto_utils.hash_password('user'),
            role=Role.USER
        ),
        User(
            username='readonly',
            password_hash=crypto_utils.hash_password('guest'),
            role=Role.READ_ONLY
        )
    ],
    'guacamole': [
        Guacamole(
            username='Admninistrator',
            password=crypto_utils.encrypt_data('password'),
            endpoint='localhost',
            datasource='mysql',
            enabled=True
        ),
    ],
    'openstack': [
        Openstack(
            auth_url='http://localhost:5000/v3',
            project_id='projectID',
            project_name='service',
            username='neutron',
            password=crypto_utils.encrypt_data('password'),
            user_domain_name='Default',
            project_domain_name='Default',
            region_name='RegionOne',
            identity_api_version='3',
            enabled=True
        )
    ],
    'saltstack': [
        Saltstack(
            endpoint='http://localhost:8080/salt/',
            username='Administrator',
            password=crypto_utils.encrypt_data('Administrator'),
            hostname='hostname',
            enabled=True
        )
    ],
    'event_logs': [
        EventLog(
            log_level=LogLevel.INFO,
            message='This is an info level log.'
        ),
        EventLog(
            log_level=LogLevel.WARNING,
            message='This is a warning level log.'
        ),
        EventLog(
            log_level=LogLevel.ERROR,
            message='This is an error level log.'
        ),
        EventLog(
            log_level=LogLevel.CRITICAL,
            message='This is a critical level log.'
        )
    ]
}


async def insert_seed_data() -> None:
    async with get_session() as db:
        for labels in SEED_DATA.keys():
            print('Inserting seed data for', labels)
            for seeds in SEED_DATA[labels]:
                db.add(seeds)
        await db.commit()


async def main() -> None:
    await connect_db()
    await insert_seed_data()

if __name__ == '__main__':
    asyncio.run(main())
