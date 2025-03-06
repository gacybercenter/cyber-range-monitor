from typing import AsyncGenerator
from fastapi.testclient import TestClient
import httpx
import pytest
from app.db.main import AsyncSessionLocal, engine 
from app.models import User, Role
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture.scope('session', autouse=True)
async def prepare_test_db() -> AsyncGenerator[None, None]:
    from app.models.base import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    test_admin = User(
        username='test_admin',
        password='test_admin',
        role=Role.ADMIN
    )
    test_user = User(
        username='test_user',
        password='test_user',
        role=Role.USER
    )
    test_read_only = User(
        username='test_read_only',
        password='test_read_only',
        role=Role.READ_ONLY
    )
    async with AsyncSessionLocal() as session:
        session.add_all([test_admin, test_user, test_read_only])
        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
        
# @pytest.fixture.scope('session')
# async def test_client() -> None:
#     from app.main import app
#     async with httpx.AsyncClient(app=app, base_url='http://test') as client:
#         yield TestClient(client)