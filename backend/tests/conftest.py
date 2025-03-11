from typing import Any, AsyncGenerator
from fastapi.testclient import TestClient
from fastapi import Response
from unittest.mock import AsyncMock, patch, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.main import AsyncSessionLocal, engine, set_db_pragmas
from app.core.db import seed
from app.extensions import redis_client
from app.auth.schemas import ClientIdentity
from app.auth.service import APIKeyProvider
from app.auth.const import AUTH_COOKIE_NAME
from app.core.schemas import AuthForm


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope='session', autouse=True)
async def connect_test_db() -> AsyncGenerator[None, None]:
    from app.core.models import Base
    await set_db_pragmas()
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


class MockRedisStore:
    def __init__(self) -> None:
        self.data = {}
        self.expirations = {}

    def clear(self) -> None:
        self.data = {}
        self.expirations = {}
 

@pytest.fixture(scope='session')
def redis_storage() -> MockRedisStore:
    return MockRedisStore()


@pytest.fixture
def mock_redis(redis_storage, monkeypatch) -> None:
    async def mock_set_key(key, value, ex=None) -> bool:
        key = redis_client.sanitize(key)
        redis_storage.data[key] = value
        if ex:
            redis_storage.expirations[key] = ex
        return True

    async def mock_get_key(key) -> Any:
        key = redis_client.sanitize(key)
        return redis_storage.data.get(key)

    async def mock_delete_key(key) -> bool:
        key = redis_client.sanitize(key)
        if key in redis_storage.data:
            del redis_storage.data[key]
        if key in redis_storage.expirations:
            del redis_storage.expirations[key]
        return True

    async def mock_set_expiration(key, ex) -> bool:
        key = redis_client.sanitize(key)
        if key in redis_storage.data:
            redis_storage.expirations[key] = ex
        return True

    async def mock_is_connected() -> bool:
        return True

    monkeypatch.setattr(redis_client, "set_key", mock_set_key)
    monkeypatch.setattr(redis_client, "get_key", mock_get_key)
    monkeypatch.setattr(redis_client, "delete_key", mock_delete_key)
    monkeypatch.setattr(redis_client, "set_expiration", mock_set_expiration)
    monkeypatch.setattr(redis_client, "is_connected", mock_is_connected)

    redis_storage.clear()
    return redis_storage


@pytest.fixture(scope='session')
def test_client() -> Any:
    from app.main import create_app
    with TestClient(app=create_app(), base_url='http://testserver') as client:
        yield client


def login_kwargs(user_type: str) -> dict:
    return {
        'url': '/auth/login/',
        'data': {
            'username': user_type,
            'password': user_type
        }
    }


def signin_as(user_type: str, test_client: TestClient) -> str:
    response = test_client.post(**login_kwargs(user_type))
    assert response.status_code == 200, f'Credentials for {user_type} which are known to work were rejected.'
    api_key = response.cookies.get('api_key')
    assert api_key is not None, f'The api_key is None for {user_type} when it should be present in response'
    return api_key


@pytest.fixture(scope='session')
def test_admin_key(test_client: TestClient) -> str:
    return signin_as('admin', test_client)


@pytest.fixture(scope='session')
def test_user_key(test_client: TestClient) -> str:
    return signin_as('user', test_client)


@pytest.fixture
def test_guest_key(async_test_client: TestClient) -> str:
    return signin_as('guest', async_test_client)



@pytest.fixture
def mock_client_identity() -> ClientIdentity:
    """Create a client identity for auth testing."""
    return ClientIdentity(
        user_agent="Test User Agent",
        client_ip="127.0.0.1",
        mapped_user=None
    )


@pytest.fixture
def mock_auth_form() -> AuthForm:
    """Create a mock authentication form for testing."""
    return AuthForm(
        username="test_user",
        password="test_password"
    )


@pytest.fixture
def api_key_provider() -> APIKeyProvider:
    """Create an APIKeyProvider instance for testing."""
    return APIKeyProvider(cookie_name=AUTH_COOKIE_NAME)


@pytest.fixture
def mock_response() -> Response:
    """Create a mock FastAPI response."""
    class MockResponse(Response):
        def __init__(self) -> None:
            self.deleted_cookies = []
            self.cookies = {}

        def delete_cookie(self, key) -> None:
            self.deleted_cookies.append(key)

        def set_cookie(self, **kwargs) -> None:
            self.cookies[kwargs.get('key')] = kwargs
            cookie_value = f"{kwargs.get('key')}={kwargs.get('value')}; Path=/"
            if kwargs.get('httponly'):
                cookie_value += "; HttpOnly"
            if kwargs.get('secure'):
                cookie_value += "; Secure"
            if kwargs.get('samesite'):
                cookie_value += f"; SameSite={kwargs.get('samesite')}"

            self.headers["set-cookie"] = cookie_value

    return MockResponse()


@pytest.fixture
def mock_user() -> MagicMock:
    """Create a mock user for testing."""
    user = MagicMock()
    user.username = "test_user"
    user.role = "user"
    return user
