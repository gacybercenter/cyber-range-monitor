from typing import Any
import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request

from app import config
from app.auth.schemas import APIKeyData, ClientIdentity, KeyBearerIdentity
from app.auth.api_key_store import APIKeyStore
from app.auth.service import KeyBearerService





@pytest.fixture
def mock_key_store() -> APIKeyStore:
    """Fixture for mocking APIKeyStore"""
    key_store = AsyncMock(spec=APIKeyStore)
    return key_store


@pytest.fixture
def api_key_provider(mock_key_store) -> KeyBearerService:
    """Fixture for creating an APIKeyProvider instance with a mock key store"""
    return KeyBearerService(key_store=mock_key_store)


@pytest.fixture
def api_key_payload(client_identity: ClientIdentity) -> APIKeyData:
    """Fixture for creating a sample APIKeyData"""
    return APIKeyData(
        identity=KeyBearerIdentity(
            username="testuser",
            role="admin",
        ),
        created_at=time.time(),
        client_identity=client_identity
    )




@pytest.fixture
def mock_request() -> Request:
    """Fixture for mocking FastAPI Request"""
    request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = "192.168.1.1"
    request.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    return request


@pytest.mark.asyncio
async def test_create_client_identity_from_request(mock_request) -> Any:
    """Test creating a ClientIdentity from a request"""
    client_identity = await ClientIdentity.create(mock_request)

    assert client_identity.client_ip == "192.168.1.1"
    assert client_identity.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@pytest.mark.asyncio
async def test_create_client_identity_with_forwarded_ip(mock_request) -> Any:
    """Test creating a ClientIdentity from a request with X-Forwarded-For header"""
    mock_request.headers["X-Forwarded-For"] = "10.0.0.1, 10.0.0.2"

    client_identity = await ClientIdentity.create(mock_request)

    assert client_identity.client_ip == "10.0.0.1"
    assert client_identity.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


@pytest.mark.asyncio
async def test_client_identity_equality() -> Any:
    """Test ClientIdentity equality comparison"""
    client1 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )

    client2 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )

    client3 = ClientIdentity(
        client_ip="192.168.1.2",
        user_agent="Mozilla/5.0",
    )

    assert client1 == client2
    assert not (client1 == client3)


@pytest.mark.asyncio
async def test_create_api_key_payload() -> Any:
    """Test creating an APIKeyData"""
    client_identity = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
    )

    with patch('time.time', return_value=1000.0):
        payload = APIKeyData.create(
            username="testuser",
            role="admin",
            client_identity=client_identity
        )

    assert payload.identity.username == "testuser"
    assert payload.identity.role == "admin"
    assert payload.created_at == 1000.0
    assert payload.client_identity == client_identity


@pytest.mark.asyncio
async def test_api_key_payload_trusts_client() -> Any:
    """Test APIKeyData trusts_client method"""
    client1 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0"
    )

    client2 = ClientIdentity(
        client_ip="192.168.1.2",
        user_agent="Firefox/89.0",
    )

    payload = APIKeyData(
        identity=KeyBearerIdentity(
            username="user1",
            role="admin"
        ),
        created_at=time.time(),
        client_identity=client1
    )

    assert payload.trusts_client(client1)
    assert not payload.trusts_client(client2)



@pytest.mark.asyncio
async def test_get_key_data_invalid_format(api_key_provider, mock_key_store, client_identity) -> Any:
    """Test retrieving key data with a payload that doesn't match APIKeyData schema"""
    mock_key_store.get_key_data.return_value = {"invalid": "data"}

    result = await api_key_provider.get_key_data("signed_key_123", client_identity)

    assert result is None

    mock_key_store.get_key_data.assert_called_once_with("signed_key_123")
    mock_key_store.refresh_key_exp.assert_not_called()



@pytest.mark.asyncio
async def test_get_key_data_session_hijacked(api_key_provider: KeyBearerService, mock_key_store: APIKeyStore, api_key_payload: APIKeyData, client_identity) -> None:
    """Test retrieving key data when session hijacking is detected"""
    mock_key_store.get_key_data.return_value = api_key_payload.model_dump()

    api_key_payload.created_at = time.time() - 3600  # 1 hour ago

    hijacker_identity = ClientIdentity(
        client_ip="10.0.0.1",
        user_agent="Different Browser",
    )

    result = await api_key_provider.get_key_data("signed_key_123", hijacker_identity)

    assert result is None

    mock_key_store.get_key_data.assert_called_once_with("signed_key_123")
    mock_key_store.delete_key.assert_called_once_with("signed_key_123")
    mock_key_store.extend_key_lifetime.assert_not_called()



