from sqlalchemy.ext.asyncio import AsyncSession
from api.models import User, Guacamole, Openstack, Saltstack, LogLevel, EventLog
from api.models.user import UserRoles
from api.utils.security.hashing import hash_pwd
from .logging import LogWriter


logger = LogWriter('DB_SEEDER')


def user_defaults() -> dict[str, User]:
    defaults = {
        'admin_user': User(
            username='Admin',
            role=UserRoles.admin.value,
            password_hash=hash_pwd('password')
        ),
        'read_only_user': User(
            username='ReadOnlyUser',
            role=UserRoles.read_only,
            password_hash=hash_pwd('password')
        ),
        'default_user': User(
            username='DefaultUser',
            role=UserRoles.user,
            password_hash=hash_pwd('password')
        )
    }
    return defaults


def guac_default() -> dict[str, Guacamole]:
    return {
        'guac_default': Guacamole(
            endpoint='http://localhost:8080/guacamole/',
            username='Admin',
            password='Admin',
            datasource='mysql',
            enabled=True
        )
    }


def openstack_default() -> dict[str, Openstack]:
    return {
        'openstack_default': Openstack(
            auth_url='http://localhost:8080/openstack/',
            project_id='projectID',
            project_name='service',
            username='neutron',
            password='password',
            user_domain_name='Default',
            project_domain_name='Default',
            region_name='RegionOne',
            identity_api_version='3',
            enabled=True
        )
    }


def event_log_defaults() -> dict[str, EventLog]:
    return {
        f'default_log_{level}': EventLog(
            log_level=level,
            message=f'This is a {level} message'
        )
        for level in LogLevel
    }


def saltstack_default() -> dict[str, Saltstack]:
    return {
        'saltstack_default': Saltstack(
            endpoint='http://localhost:8080/saltstack/',
            username='Adminstrator',
            password='Adminstrator',
            hostname='hostname',
            enabled=True
        )
    }


async def insert_table_defaults(session: AsyncSession) -> None:
    '''seeds the database with the default values for each of the tables'''
    logger.debug('Seeding database with default values...')

    defaults = [
        user_defaults(),
        saltstack_default(),
        openstack_default(),
        guac_default(),
        event_log_defaults()
    ]
    for labeled_defaults in defaults:
        for label, default in labeled_defaults.items():
            logger.debug(f'Adding the "{label}" to the database...')
            logger.debug(f'REPR {default}')
            session.add(default)
    await session.commit()
    logger.debug('Database seeded successfully')
