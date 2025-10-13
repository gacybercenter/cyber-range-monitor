import logging
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from range_monitor.infra.security import CryptoService


async def seed_users_table(db: AsyncSession, crypto_service: 'CryptoService'):
    from range_monitor.users.repo import User, UserRepository, UserRoles

    repo = UserRepository(db)
    for role in list(UserRoles):
        if not await repo.is_username_unique(role.value):
            continue

        new_user = User(
            username=role.value,
            password_hash=crypto_service.hash_password(role.value),
            role=role,
            created_by='system',
        )
        db.add(new_user)


async def seed_datasources(db: AsyncSession, crypto_service: 'CryptoService'):
    from range_monitor.sources.models import (
        Guacamole,
        Openstack,
        Saltstack,
    )

    default_password = crypto_service.encrypt_text('password')

    guac = Guacamole(
        label='default-guac',
        username='defaultguac',
        password_cipher=default_password,
        hostname='http://localhost:8080/guacamole',
        description='Default Guacamole datasource',
        data_source_type='mysql',
    )

    openstack = Openstack(
        label='default-openstack',
        auth_url='http://localhost:5000/v3',
        password_cipher=default_password,
        username='defaultopenstack',
        user_domain_name='Default',
        description='Default OpenStack datasource',
        region_name='RegionOne',
        identity_api_version='3',
        project_name='demo',
    )

    saltstack = Saltstack(
        label='default-saltstack',
        username='defaultsalt',
        password_cipher=default_password,
        endpoint='http://localhost:8000',
        hostname='localhost',
        description='Default SaltStack datasource',
    )

    db.add_all([guac, openstack, saltstack])


async def insert_seed_data(db: AsyncSession, crypto_service: 'CryptoService') -> None:
    logger = logging.getLogger(__name__)
    logger.info('Inserting seed data into the database...')
    await seed_users_table(db, crypto_service)
    logger.info('Seeded users table.')
    await seed_datasources(db, crypto_service)
    logger.info('Seeded datasources table.')
    await db.commit()
