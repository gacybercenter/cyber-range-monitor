import logging

from sqlalchemy.ext.asyncio import AsyncSession

from server.app import security


async def seed_users_table(db: AsyncSession) -> None:
    from server.app.users import repo as user_cmd
    from server.db.repos import SQLRepository
    from server.enums import UserRoles
    from server.models import User

    repo = SQLRepository(
        model=User,
        db=db,
    )
    for role in list(UserRoles):
        if not await user_cmd.is_username_unique(
            repo,
            username=role.value,
        ):
            continue

        new_user = User(
            username=role.value,
            password_hash=security.hash_password(role.value),
            role=role,
            created_by='system',
        )
        db.add(new_user)


def seed_datasources(db: AsyncSession) -> None:
    from server.models import (
        Guacamole,
        Openstack,
        Saltstack,
    )

    default_password = security.encrypt_plaintext('password')

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


async def insert_seed_data(db: AsyncSession) -> None:
    logger = logging.getLogger(__name__)
    logger.info('Inserting seed data into the database...')
    await seed_users_table(db)
    logger.info('Seeded users table.')
    seed_datasources(db)
    logger.info('Seeded datasources table.')
    await db.commit()


def main() -> None:
    import asyncio

    from server.db.sql import create_tables, get_session

    print("""
**********************
scripts.seed
**********************
This script seeds the database with initial data.
    """)

    async def run() -> None:
        await create_tables()
        async with get_session() as session:
            await insert_seed_data(session)

    asyncio.run(run())


if __name__ == '__main__':
    main()
