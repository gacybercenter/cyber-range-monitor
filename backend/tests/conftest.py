import json
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.core.db import seed
from range_monitor.core.db.main import AsyncSessionLocal, engine
from range_monitor.core.schemas import AuthForm
from range_monitor.sessions.schemas import ClientIdentity


@pytest_asyncio.fixture(scope='session', autouse=True)
async def connect_test_db() -> AsyncGenerator[None, None]:
    from range_monitor.core.db.base import BaseModel

    async with engine.begin() as conn:

        await conn.run_sync(BaseModel.metadata.drop_all)
        await conn.run_sync(BaseModel.metadata.create_all)
    await seed.default_seed()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'


@pytest_asyncio.fixture(scope='session')
async def connect_test_redis() -> Any:
    from range_monitor.extensions.redis.connection import RedisConnection

    is_connected = await RedisConnection.connect()
    assert is_connected, 'Failed to connect to Redis'
    yield
    await RedisConnection.disconnect()


@pytest.fixture
def test_client() -> Any:
    """Create a fresh test client for each test to avoid state leakage between tests"""
    from range_monitor.app import app

    with TestClient(app=app) as client:
        yield client


def login_kwargs(user_type: str) -> dict:
    return {'url': '/auth/', 'json': {'username': user_type, 'password': user_type}}


def signin_as(user_type: str, test_client: TestClient) -> str:
    """Sign in as a specified user type and return the API key"""
    login_data = {'username': user_type, 'password': user_type}

    response = test_client.post(
        url='/auth/', json=login_data, headers={'Content-Type': 'application/json'}
    )

    print(f'Login response status: {response.status_code}')
    try:
        print(f'Login response: {json.dumps(response.json(), indent=2)}')
        api_key = response.json().get('apiKey')
        assert api_key is not None, (
            f'The api_key is None for {user_type} when it should be present in response'
        )
        return api_key
    except json.JSONDecodeError:
        print(f'Raw response content: {response.content}')
        raise


@pytest.fixture
def test_admin_key(test_client: TestClient) -> str:
    return signin_as('admin', test_client)


@pytest.fixture
def test_guest_key(test_client: TestClient) -> str:
    return signin_as('guest', test_client)


@pytest.fixture
def test_user_key(test_client: TestClient) -> str:
    return signin_as('admin', test_client)


@pytest.fixture
def test_admin_client(test_client: TestClient) -> TestClient:
    """Create a client with admin authentication"""
    key = signin_as('admin', test_client)
    # Create a new client to avoid modifying the session-scoped one
    test_client.headers.update({'Authorization': f'Bearer {key}'})
    return test_client


@pytest.fixture
def test_user_client(test_client: TestClient) -> TestClient:
    """Create a client with user authentication"""
    key = signin_as('user', test_client)
    test_client.headers.update({'Authorization': f'Bearer {key}'})
    return test_client


@pytest.fixture
def test_guest_client(test_client: TestClient) -> TestClient:
    """Create a client with guest authentication"""
    key = signin_as('guest', test_client)
    test_client.headers.update({'Authorization': f'Bearer {key}'})
    return test_client


@pytest.fixture
def mock_auth_form() -> AuthForm:
    """Create a mock authentication form for testing."""
    return AuthForm(username='user', password='user')


@pytest.fixture
def client_identity() -> ClientIdentity:
    """Fixture for creating a sample ClientIdentity"""
    return ClientIdentity(
        client_ip='192.168.1.1',
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    )
