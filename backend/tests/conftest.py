from typing import Any, AsyncGenerator
from fastapi.testclient import TestClient

from httpx import ASGITransport, AsyncClient


import pytest
from app.core.db.main import AsyncSessionLocal, engine
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.main import AsyncSessionLocal, engine, set_db_pragmas
from app.core.db import seed


pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='session', autouse=True)
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


@pytest.mark.asyncio
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session')
def async_test_client() -> Any:
    from app.main import app
    with TestClient(app=app, base_url='http://testserver') as client:
        yield client


@pytest.fixture(scope='session')
def test_client() -> Any:
    from app.main import app
    yield TestClient(app=app, base_url='http://testserver')


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
