import pytest
import time
from unittest.mock import patch

from app.auth.schemas import APIKeyPayload, ClientIdentity
from app.extensions.security import crypto
from app.auth import redis_key_store
from app import config


@pytest.mark.asyncio
async def test_create_signed_key(api_key_provider) -> None:
    """Test creating a signed API key."""
    signed_key, raw_key = api_key_provider.create_signed_key()

    unsigned = crypto.load_signature(signed_key)
    assert unsigned == raw_key
    assert len(raw_key) > 20


@pytest.mark.asyncio
async def test_cookie_params(api_key_provider) -> None:
    """Test generating cookie parameters with the correct options."""
    signed_key = "test-signed-key"
    params = api_key_provider.cookie_params(signed_key)

    assert params["key"] == api_key_provider.cookie_name
    assert params["value"] == signed_key

    assert "httponly" in params
    assert "secure" in params
    assert "samesite" in params


@pytest.mark.asyncio
async def test_key_max_age_reached(api_key_provider) -> None:
    """Test detection of keys that have reached maximum age."""
    key_config = config.get_api_key_config()

    recent_key = APIKeyPayload(
        username="test_user",
        role="user",
        client_identity=ClientIdentity(
            user_agent="test_agent",
            client_ip="127.0.0.1",
            mapped_user="test_user"
        ),
        created_at=time.time()
    )

    assert not api_key_provider.key_max_age_reached(recent_key), "Key should not be expired"

    expired_time = time.time() - key_config.key_max_lifetime() - 100
    expired_key = APIKeyPayload(
        username="test_user",
        role="user",
        client_identity=ClientIdentity(
            user_agent="test_agent",
            client_ip="127.0.0.1",
            mapped_user="test_user"
        ),
        created_at=expired_time
    )

    assert api_key_provider.key_max_age_reached(expired_key), "Key should've expired"


@pytest.mark.asyncio
async def test_resolve_signature(api_key_provider) -> None:
    """Test resolution of signed API keys."""
    raw_key = "test-raw-key"
    signed_key = crypto.create_signature(raw_key)

    resolved = api_key_provider.resolve_signature(signed_key)
    assert resolved == raw_key, "Resolved key should match the original raw key"

    invalid_key = "invalid-signature-not-generated-by-crypto"
    resolved = api_key_provider.resolve_signature(invalid_key)
    assert resolved is None, "Invalid signature should resolve to None"

    with patch("app.extensions.security.crypto.load_signature",
               side_effect=Exception("Signature expired")):
        resolved = api_key_provider.resolve_signature(signed_key)
        assert resolved is None


@pytest.mark.asyncio
async def test_store_api_key(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test storing an API key in Redis."""
    payload = APIKeyPayload(
        username="test_user",
        role="user",
        client_identity=mock_client_identity,
        created_at=time.time()
    )

    signed_key = await api_key_provider.store_api_key(payload)

    assert signed_key is not None
    assert len(signed_key) > 20

    assert len(mock_redis.data) == 1

    redis_key = list(mock_redis.data.keys())[0]
    assert redis_key.startswith("api_key:")


@pytest.mark.asyncio
async def test_create_key_cookie(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test creating a key cookie for a user."""
    cookie_params = await api_key_provider.create_key_cookie(
        username="test_user",
        role="user",
        client_identity=mock_client_identity
    )

    assert cookie_params["key"] == api_key_provider.cookie_name
    assert "value" in cookie_params
    assert cookie_params.get("httponly") is True

    assert len(mock_redis.data) == 1


@pytest.mark.asyncio
async def test_get_payload_valid(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test retrieving a valid API key payload."""
    cookie_params = await api_key_provider.create_key_cookie(
        username="test_user",
        role="user",
        client_identity=mock_client_identity
    )

    signed_key = cookie_params["value"]

    payload = await api_key_provider.get_payload(
        signed_key=signed_key,
        inbound_client=mock_client_identity
    )

    assert payload is not None, 'Payload should not be None'
    assert payload.username == "test_user", 'Username should match'
    assert payload.role == "user", 'Role should match'
    assert payload.client_identity.user_agent == mock_client_identity.user_agent, 'User agent should match'
    assert payload.client_identity.client_ip == mock_client_identity.client_ip, 'IP address should match'


@pytest.mark.asyncio
async def test_get_payload_invalid_signature(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test retrieving a payload with an invalid signature."""
    invalid_key = "invalid-signature"

    payload = await api_key_provider.get_payload(
        signed_key=invalid_key,
        inbound_client=mock_client_identity
    )

    assert payload is None, 'Payload should be None for invalid signature'


@pytest.mark.asyncio
async def test_get_payload_nonexistent_key(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test retrieving a payload for a key that doesn't exist in Redis."""
    raw_key = "test-raw-key"
    signed_key = crypto.create_signature(raw_key)

    payload = await api_key_provider.get_payload(
        signed_key=signed_key,
        inbound_client=mock_client_identity
    )

    assert payload is None, 'Payload should be None for non-existent key'


@pytest.mark.asyncio
async def test_get_payload_session_hijacked(api_key_provider, mock_redis) -> None:
    """Test retrieving a payload with a different client identity (session hijacking)."""
    original_client = ClientIdentity(
        user_agent="Original Browser",
        client_ip="192.168.1.1",
        mapped_user="test_user"
    )

    cookie_params = await api_key_provider.create_key_cookie(
        username="test_user",
        role="user",
        client_identity=original_client
    )

    signed_key = cookie_params["value"]

    hijacker_client = ClientIdentity(
        user_agent="Different Browser",
        client_ip="10.0.0.1",
        mapped_user=None
    )

    payload = await api_key_provider.get_payload(
        signed_key=signed_key,
        inbound_client=hijacker_client
    )

    assert payload is None, 'Payload should be None for hijacked session'

    unsigned_key = api_key_provider.resolve_signature(signed_key)
    key_in_redis = f"api_key:{unsigned_key}"

    assert key_in_redis not in mock_redis.data, 'Key should not be in Redis for hijacked session'


@pytest.mark.asyncio
async def test_delete_key(api_key_provider, mock_redis, mock_client_identity) -> None:
    """Test deleting an API key."""
    cookie_params = await api_key_provider.create_key_cookie(
        username="test_user",
        role="user",
        client_identity=mock_client_identity
    )

    signed_key = cookie_params["value"]

    assert len(mock_redis.data) == 1, "Key should be in Redis"

    await api_key_provider.delete_key(signed_key)

    assert len(mock_redis.data) == 0, 'Key should be deleted from Redis'


@pytest.mark.asyncio
async def test_revoke_key(api_key_provider, mock_redis, mock_client_identity, mock_response) -> None:
    """Test revoking an API key and clearing the cookie."""
    cookie_params = await api_key_provider.create_key_cookie(
        username="test_user",
        role="user",
        client_identity=mock_client_identity
    )

    signed_key = cookie_params["value"]

    assert len(mock_redis.data) == 1, "Key should be in Redis"

    await api_key_provider.revoke_key(signed_key, mock_response)

    assert len(mock_redis.data) == 0, 'Key should be deleted from Redis'

    assert api_key_provider.cookie_name in mock_response.deleted_cookies, 'Cookie should be deleted'


@pytest.mark.asyncio
async def test_redis_key_store_functions(mock_redis) -> None:
    """Test the redis_key_store functions directly."""
    await redis_key_store.set_api_key("test-key", {"test": "data"}, ex=3600)

    prefixed_key = redis_key_store.api_key_prefix("test-key")
    assert prefixed_key in mock_redis.data, "Key not set correctly"

    data = await redis_key_store.get_api_key("test-key")
    assert data == {"test": "data"}, "Key retrieved with a different value"

    await redis_key_store.set_key_exp("test-key", 7200)
    assert mock_redis.expirations[prefixed_key] == 7200

    await redis_key_store.delete_api_key("test-key")
    assert prefixed_key not in mock_redis.data
