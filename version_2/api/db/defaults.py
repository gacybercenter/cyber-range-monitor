from fastapi.background import P
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import User, Guacamole, Openstack, Saltstack, LogLevel, EventLog
from api.models.user import UserRoles
from api.utils.security.hashing import hash_pwd
from .logging import LogWriter


logger = LogWriter('DB_SEEDER')


class db_seed:
    user: dict[str, dict] = {
        'admin': {
            'username': 'Admin',
            'role': UserRoles.admin.value,
            'password_hash': hash_pwd('password')
        },
        'read_only': {
            'username': 'ReadOnlyUser',
            'role': UserRoles.read_only.value,
            'password_hash': hash_pwd('password')
        },
        'user': {
            'username': 'DefaultUser',
            'role': UserRoles.user.value,
            'password_hash': hash_pwd('password')
        }
    }

    guac: dict[str, dict] = {
        'base': {
            'endpoint': 'http://localhost:8080/guacamole/',
            'username': 'Admin',
            'password': 'Admin',
            'datasource': 'mysql',
            'enabled': True
        }
    }

    openstack: dict[str, dict] = {
        'base': {
            'auth_url': 'http://localhost:8080/openstack/',
            'project_id': 'projectID',
            'project_name': 'service',
            'username': 'neutron',
            'password': 'password',
            'user_domain_name': 'Default',
            'project_domain_name': 'Default',
            'region_name': 'RegionOne',
            'identity_api_version': '3',
            'enabled': True
        }
    }

    saltstack: dict[str, dict] = {
        'base': {
            'endpoint': 'http://localhost:8080/saltstack/',
            'username': 'Adminstrator',
            'password': 'Adminstrator',
            'hostname': 'hostname',
            'enabled': True
        }
    }

    @staticmethod
    def log_defaults() -> dict[str, dict]:
        return {
            f'default_log_{level}': {
                'log_level': level,
                'message': f'This is a {level} log',
            }
            for level in LogLevel
        }


async def insert_table_defaults(session: AsyncSession) -> None:
    '''
    seeds the database with the default values for each of the tables
    '''
    logger.debug(
        'seeding database with default values defined in the "db_seed"'
    )
    default_model_map: list[tuple] = [
        (db_seed.user, User),
        (db_seed.guac, Guacamole),
        (db_seed.openstack, Openstack),
        (db_seed.saltstack, Saltstack),
        (db_seed.log_defaults(), EventLog)
    ]

    for seed_data, model_type in default_model_map:
        for labels in seed_data.keys():
            logger.debug(f'Inserting default values for {model_type.__name__}')
            new_instance = model_type(**seed_data[labels])
            session.add(new_instance)
            await session.commit()

    logger.debug('Database seeded successfully')
