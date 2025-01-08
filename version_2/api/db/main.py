from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text 
import os
from api.config.settings import app_config

# _PRAGMAS: dict = {
#     "journal_mode": "WAL",
#     "foreign_keys": "ON",
#     "busy_timeout": 5000
# }
    
_CONNECT_ARGS: dict = {
    "check_same_thread": False,
    "timeout": 30,
}

engine = create_async_engine(
    url=app_config.DATABASE_URL,
    echo=app_config.DATABASE_ECHO,
    connect_args=_CONNECT_ARGS,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    '''base model; all ORM models MUST inherit from this class'''
    pass

async def init_db() -> None:
    '''_summary_
    Creates / Initializes the SQLite database using the engine, uses
    the presence of the 'instance' directory to determine if the tables
    were already created and if not seeds the database with defaults for all
    tables
    '''
    table_exists = os.path.exists('instance')
    os.makedirs('instance', exist_ok=True)
    
    async with engine.begin() as conn:
        from api.models import User, Guacamole, Openstack, Saltstack
        await conn.run_sync(Base.metadata.create_all)
        
    if not table_exists:
        await seed_db()


async def get_db() -> AsyncSession:  # type: ignore
    '''yields a single async session'''
    async with SessionLocal() as session:
        yield session # type: ignore


async def seed_db() -> None:
    '''seeds the database with the default values for each of the tables'''
    from api.models import User, Guacamole, Openstack, Saltstack
    from api.models.user import UserRoles

    defaults = {
        'user': User(
            username='Adminstrator',
            permission=UserRoles.admin.value,
            password_hash='scrypt:32768:8:1$OZrgrecSOwvEYxBR$b7b5fc887dc6a227c8eb35e22c602e5a62f9305d8458a898bf42a920b84e03b282d8187410d5ad989af71d1120c7b5213466afb42d1a133100101ea06a02da1e'
        ),
        'guac': Guacamole(
            endpoint='http://localhost:8080/guacamole/',
            username='Adminstrator',
            password='Adminstrator',
            datasource='mysql',
            enabled=True,
        ),
        'openstack': Openstack(
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
        ),
        'saltstack': Saltstack(
            endpoint='http://localhost:8080/saltstack/',
            username='Adminstrator',
            password='Adminstrator',
            hostname='hostname',
            enabled=True
        )
    }
    async with SessionLocal() as session:
        for model_name, default in defaults.items():
            print(f'[>] Seeding default data for {model_name}')
            session.add(default)
            await session.commit()
        print('[+] Seeding complete')

# async def set_db_pragmas() -> None:
#     global engine, _PRAGMAS
#     async with engine.begin() as conn:
#         for pragma, value in _PRAGMAS.items():
#             await conn.execute(text(f'PRAGMA {pragma} = {value}'))
