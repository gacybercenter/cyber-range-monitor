from typing import Any, AsyncGenerator

from fastapi.testclient import TestClient

import pytest

import pytest_asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import ClientIdentity
from app.auth.const import AUTH_COOKIE_NAME

from app.core.db.main import AsyncSessionLocal, engine
from app.core.db import seed

from app.core.schemas import AuthForm




@pytest_asyncio.fixture(scope='session', autouse=True)
async def connect_test_db() -> AsyncGenerator[None, None]:
    from app.core.db.const import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed.default_seed()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'

@pytest_asyncio.fixture(scope='session')
async def connect_test_redis() -> Any:
    from app.extensions.redis.connection import RedisConnection
    is_connected = await RedisConnection.connect()
    assert is_connected, 'Failed to connect to Redis'
    yield 
    await RedisConnection.disconnect()
    



@pytest.fixture(scope='session')
def test_client() -> Any:
    from app.main import create_app
    with TestClient(app=create_app()) as client:
        yield client 

    

def login_kwargs(user_type: str) -> dict:
    return {
        'url': '/auth/login/',
        'data': {'username': user_type, 'password': user_type}
    }

def signin_as(user_type: str, test_client: TestClient) -> str:
    response = test_client.post(**login_kwargs(user_type))
    assert response.status_code == 200, f'Credentials for {user_type} which are known to work were rejected.'
    api_key = response.cookies.get(AUTH_COOKIE_NAME)
    assert api_key is not None, f'The api_key is None for {user_type} when it should be present in response'
    return api_key


@pytest.fixture
def test_admin_key(test_client: TestClient) -> str:
    return signin_as('admin', test_client)


@pytest.fixture
def test_user_key(test_client: TestClient) -> str:
    return signin_as('user', test_client)


@pytest.fixture
def test_guest_key(test_client: TestClient) -> str:
    return signin_as('guest', test_client)



@pytest.fixture
def mock_auth_form() -> AuthForm:
    """Create a mock authentication form for testing."""
    return AuthForm(username="user", password="user")

@pytest.fixture
def client_identity() -> ClientIdentity:
    """Fixture for creating a sample ClientIdentity"""
    return ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        mapped_user="testuser"
    )



