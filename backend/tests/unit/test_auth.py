from datetime import datetime
from typing import Any
import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import Request

from app.auth.schemas import APIKeyData, ClientIdentity, KeyBearerIdentity
from app.auth.api_key_store import APIKeyStore
from app.auth.service import KeyBearerService
from app.auth.const import KEY_EXPIRATION, KEY_MAX_LIFETIME


@pytest.fixture
def mock_key_store() -> APIKeyStore:
    """Fixture for mocking APIKeyStore"""
    key_store = AsyncMock(spec=APIKeyStore)
    return key_store


@pytest.fixture
def api_key_provider(mock_key_store: APIKeyStore) -> KeyBearerService:
    """Fixture for creating an APIKeyProvider instance with a mock key store"""
    return KeyBearerService(key_store=mock_key_store)


@pytest.fixture
def api_key_data(client_identity: ClientIdentity) -> APIKeyData:
    """Fixture for creating a sample APIKeyData"""
    return APIKeyData(
        identity=KeyBearerIdentity(
            username='testuser',
            role='admin',
        ),
        created_at=time.time(),
        client_identity=client_identity,
    )


def get_key_timestamps(key_data: APIKeyData) -> tuple[datetime, datetime]:
    key_expires = datetime.fromtimestamp(key_data.created_at + KEY_EXPIRATION)
    key_max_age = datetime.fromtimestamp(key_data.created_at + KEY_MAX_LIFETIME)
    return key_expires, key_max_age


@pytest.fixture
def mock_request() -> Request:
    """Fixture for mocking FastAPI Request"""
    request: Request = MagicMock(spec=Request)
    request.client = MagicMock()
    request.client.host = '192.168.1.1'
    request.headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    return request


@pytest.mark.asyncio
@pytest.mark.unit
class TestAuthUnit:
    async def test_create_client_identity(self, mock_request) -> Any:
        """Test creating a ClientIdentity from a request"""
        client_identity = await ClientIdentity.create(mock_request)

        assert client_identity.client_ip == '192.168.1.1'
        assert (
            client_identity.user_agent
            == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    async def test_create_identity_with_forwarded(self, mock_request) -> Any:
        """Test creating a ClientIdentity from a request with X-Forwarded-For header"""
        mock_request.headers['X-Forwarded-For'] = '10.0.0.1, 10.0.0.2'

        client_identity = await ClientIdentity.create(mock_request)

        assert client_identity.client_ip == '10.0.0.1'
        assert (
            client_identity.user_agent
            == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )

    async def test_client_identity_equality(self) -> Any:
        """Test ClientIdentity equality comparison"""
        client1 = ClientIdentity(
            client_ip='192.168.1.1',
            user_agent='Mozilla/5.0',
        )

        client2 = ClientIdentity(
            client_ip='192.168.1.1',
            user_agent='Mozilla/5.0',
        )

        client3 = ClientIdentity(
            client_ip='192.168.1.2',
            user_agent='Mozilla/5.0',
        )

        assert client1 == client2, 'Client Identities should match'
        assert not (client1 == client3), 'Client Identities should not match'

    async def test_create_api_key_data(self) -> Any:
        """Test creating an APIKeyData"""
        client_identity = ClientIdentity(
            client_ip='192.168.1.1',
            user_agent='Mozilla/5.0',
        )

        with patch('time.time', return_value=1000.0):
            payload = APIKeyData.create(
                username='testuser', role='admin', client_identity=client_identity
            )

        assert payload.identity.username == 'testuser'
        assert payload.identity.role == 'admin'
        assert payload.created_at == 1000.0
        assert payload.client_identity == client_identity

    async def test_key_hijacking_prevention(self) -> Any:
        """Test APIKeyData trusts_client method"""
        client1 = ClientIdentity(client_ip='192.168.1.1', user_agent='Mozilla/5.0')

        client2 = ClientIdentity(
            client_ip='192.168.1.2',
            user_agent='Firefox/89.0',
        )

        payload = APIKeyData(
            identity=KeyBearerIdentity(username='user1', role='admin'),
            created_at=time.time(),
            client_identity=client1,
        )

        assert payload.trusts_client(client1)
        assert not payload.trusts_client(client2)

    async def test_get_key_data_invalid_format(
        self, api_key_provider, mock_key_store, client_identity
    ) -> Any:
        """Test retrieving key data with a payload that doesn't match APIKeyData schema"""
        mock_key_store.get_key_data.return_value = {'invalid': 'data'}
        result = await api_key_provider.get_key_data('signed_key_123', client_identity)
        assert result is None

    async def test_get_key_hijacked(
        self,
        api_key_provider: KeyBearerService,
        mock_key_store: APIKeyStore,
        api_key_data: APIKeyData,
    ) -> None:
        """Test retrieving key data when session hijacking is detected"""
        mock_key_store.get_key_data.return_value = api_key_data.model_dump()

        api_key_data.created_at = time.time() - 3600  # 1 hour ago

        hijacker_identity = ClientIdentity(
            client_ip='10.0.0.1',
            user_agent='Different Browser',
        )

        result = await api_key_provider.get_key_data(
            'signed_key_123', hijacker_identity
        )

        assert result is None

        mock_key_store.extend_key_lifetime.assert_not_called()
