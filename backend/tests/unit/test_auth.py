from typing import Any
import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Response, Request

from app import config
from app.auth.schemas import APIKeyPayload, ClientIdentity
from app.auth.api_key_store import APIKeyStore
from app.auth.service import APIKeyProvider


@pytest.fixture
def mock_config() -> Any:
    """Mock configuration for auth settings"""
    mock_conf = MagicMock()
    mock_auth_conf = MagicMock()

    mock_auth_conf.cookie_options.return_value = {
        "httponly": True,
        "secure": True,
        "samesite": "lax",
        "path": "/"
    }

    mock_auth_conf.cookie_exp.return_value = 3600  # 1 hour
    mock_auth_conf.key_max_age.return_value = 86400  # 24 hours

    mock_conf.auth = mock_auth_conf
    mock_conf.get_config_yml.return_value = mock_conf

    with patch('app.auth.service.config', mock_conf), \
            patch('app.auth.service.auth_conf', mock_auth_conf), \
            patch('app.auth.api_key_store.auth_conf', mock_auth_conf), \
            patch('app.config', mock_conf):
        yield mock_conf


@pytest.fixture
def mock_key_store() -> APIKeyStore:
    """Fixture for mocking APIKeyStore"""
    key_store = AsyncMock(spec=APIKeyStore)
    return key_store


@pytest.fixture
def api_key_provider(mock_key_store) -> APIKeyProvider:
    """Fixture for creating an APIKeyProvider instance with a mock key store"""
    return APIKeyProvider(cookie_name="session", key_store=mock_key_store)


@pytest.fixture
def api_key_payload(client_identity: ClientIdentity) -> APIKeyPayload:
    """Fixture for creating a sample APIKeyPayload"""
    return APIKeyPayload(
        username="testuser",
        role="admin",
        created_at=time.time(),
        client_identity=client_identity
    )


@pytest.fixture
def mock_response() -> Response:
    """Fixture for mocking FastAPI Response"""
    response = MagicMock(spec=Response)
    response.delete_cookie = MagicMock()
    return response


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
    assert client_identity.mapped_user == "Unknown"


@pytest.mark.asyncio
async def test_create_client_identity_with_forwarded_ip(mock_request) -> Any:
    """Test creating a ClientIdentity from a request with X-Forwarded-For header"""
    mock_request.headers["X-Forwarded-For"] = "10.0.0.1, 10.0.0.2"

    client_identity = await ClientIdentity.create(mock_request)

    assert client_identity.client_ip == "10.0.0.1"
    assert client_identity.user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    assert client_identity.mapped_user == "Unknown"


@pytest.mark.asyncio
async def test_client_identity_equality() -> Any:
    """Test ClientIdentity equality comparison"""
    client1 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
        mapped_user="user1"
    )

    client2 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
        mapped_user="user2"
    )

    client3 = ClientIdentity(
        client_ip="192.168.1.2",
        user_agent="Mozilla/5.0",
        mapped_user="user1"
    )

    assert client1 == client2
    assert not (client1 == client3)


@pytest.mark.asyncio
async def test_create_api_key_payload() -> Any:
    """Test creating an APIKeyPayload"""
    client_identity = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
        mapped_user="Unknown"
    )

    with patch('time.time', return_value=1000.0):
        payload = APIKeyPayload.create(
            username="testuser",
            role="admin",
            client_identity=client_identity
        )

    assert payload.username == "testuser"
    assert payload.role == "admin"
    assert payload.created_at == 1000.0
    assert payload.client_identity == client_identity
    assert payload.client_identity.mapped_user == "testuser"


@pytest.mark.asyncio
async def test_api_key_payload_trusts_client() -> Any:
    """Test APIKeyPayload trusts_client method"""
    client1 = ClientIdentity(
        client_ip="192.168.1.1",
        user_agent="Mozilla/5.0",
        mapped_user="user1"
    )

    client2 = ClientIdentity(
        client_ip="192.168.1.2",
        user_agent="Firefox/89.0",
        mapped_user="user1"
    )

    payload = APIKeyPayload(
        username="user1",
        role="admin",
        created_at=time.time(),
        client_identity=client1
    )

    assert payload.trusts_client(client1)
    assert not payload.trusts_client(client2)


@pytest.mark.asyncio
async def test_auth_cookie(api_key_provider, mock_config) -> Any:
    """Test creating auth cookie parameters"""
    cookie_params = api_key_provider.auth_cookie("signed_key_123")

    assert cookie_params["key"] == "session"
    assert cookie_params["value"] == "signed_key_123"
    assert cookie_params["httponly"] is True
    assert cookie_params["secure"] is True
    assert cookie_params["samesite"] == "lax"
    assert cookie_params["path"] == "/"


@pytest.mark.asyncio
async def test_key_max_age_reached(api_key_provider, mock_config, api_key_payload) -> Any:
    """Test checking if the key max age is reached"""
    api_key_payload.created_at = time.time() - 3600
    assert api_key_provider.key_max_age_reached(api_key_payload) is False

    api_key_payload.created_at = time.time() - 100000
    assert api_key_provider.key_max_age_reached(api_key_payload) is True


@pytest.mark.asyncio
async def test_issue_key(api_key_provider, mock_key_store, client_identity, mock_config) -> Any:
    """Test issuing a new API key"""
    mock_key_store.create_key.return_value = "signed_key_123"

    with patch('time.time', return_value=1000.0):
        signed_key = await api_key_provider.issue_key(
            username="testuser",
            role="admin",
            client_identity=client_identity
        )

    assert signed_key == "signed_key_123"
    assert client_identity.mapped_user == "testuser"

    mock_key_store.create_key.assert_called_once()
    call_args = mock_key_store.create_key.call_args[0]

    payload_dict = call_args[0]
    assert payload_dict["username"] == "testuser"
    assert payload_dict["role"] == "admin"
    assert payload_dict["created_at"] == 1000.0

    assert call_args[1] == 3600


@pytest.mark.asyncio
async def test_get_key_data_valid(api_key_provider, mock_key_store, api_key_payload, client_identity) -> Any:
    """Test retrieving key data with a valid key"""
    mock_key_store.get_key_payload.return_value = api_key_payload.model_dump()

    api_key_payload.created_at = time.time() - 3600  # 1 hour ago

    result = await api_key_provider.get_key_data("signed_key_123", client_identity)

    assert result is not None
    assert result.username == api_key_payload.username
    assert result.role == api_key_payload.role

    mock_key_store.get_key_payload.assert_called_once_with("signed_key_123")
    mock_key_store.refresh_key_exp.assert_called_once_with(
        "signed_key_123", 3600)


@pytest.mark.asyncio
async def test_get_key_data_invalid_payload(api_key_provider, mock_key_store, client_identity) -> Any:
    """Test retrieving key data with an invalid payload"""
    mock_key_store.get_key_payload.return_value = None

    result = await api_key_provider.get_key_data("signed_key_123", client_identity)

    assert result is None

    mock_key_store.get_key_payload.assert_called_once_with("signed_key_123")
    mock_key_store.refresh_key_exp.assert_not_called()


@pytest.mark.asyncio
async def test_get_key_data_invalid_format(api_key_provider, mock_key_store, client_identity) -> Any:
    """Test retrieving key data with a payload that doesn't match APIKeyPayload schema"""
    mock_key_store.get_key_payload.return_value = {"invalid": "data"}

    result = await api_key_provider.get_key_data("signed_key_123", client_identity)

    assert result is None

    mock_key_store.get_key_payload.assert_called_once_with("signed_key_123")
    mock_key_store.refresh_key_exp.assert_not_called()



@pytest.mark.asyncio
async def test_get_key_data_session_hijacked(api_key_provider, mock_key_store, api_key_payload, client_identity):
    """Test retrieving key data when session hijacking is detected"""
    mock_key_store.get_key_payload.return_value = api_key_payload.model_dump()

    api_key_payload.created_at = time.time() - 3600  # 1 hour ago

    hijacker_identity = ClientIdentity(
        client_ip="10.0.0.1",
        user_agent="Different Browser",
        mapped_user="testuser"
    )

    result = await api_key_provider.get_key_data("signed_key_123", hijacker_identity)

    assert result is None

    mock_key_store.get_key_payload.assert_called_once_with("signed_key_123")
    mock_key_store.remove_key.assert_called_once_with("signed_key_123")
    mock_key_store.refresh_key_exp.assert_not_called()


@pytest.mark.asyncio
async def test_revoke_key_with_signed_key(api_key_provider, mock_key_store, mock_response) -> Any:
    """Test revoking a key with a valid signed key"""
    await api_key_provider.revoke_key("signed_key_123", mock_response)

    mock_key_store.remove_key.assert_called_once_with("signed_key_123")
    mock_response.delete_cookie.assert_called_once_with("session")


@pytest.mark.asyncio
async def test_revoke_key_without_signed_key(api_key_provider, mock_key_store, mock_response) -> Any:
    """Test revoking a key without a signed key"""
    await api_key_provider.revoke_key(None, mock_response)

    mock_key_store.remove_key.assert_not_called()
    mock_response.delete_cookie.assert_called_once_with("session")