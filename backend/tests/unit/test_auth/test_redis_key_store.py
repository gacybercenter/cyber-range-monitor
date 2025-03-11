import pytest
import json
from unittest.mock import patch

from app.auth import redis_key_store
from app.extensions.security import crypto



@pytest.mark.asyncio
async def test_set_api_key(mock_redis) -> None:
    """Test setting an API key in Redis with encryption."""
    test_data = {"username": "test_user", "role": "user"}

    await redis_key_store.set_api_key("test-key", test_data, ex=3600)

    prefixed_key = redis_key_store.api_key_prefix("test-key")
    assert prefixed_key in mock_redis.data

    stored_data = mock_redis.data[prefixed_key]
    assert stored_data != json.dumps(test_data)  

    decrypted = crypto.decrypt_data(stored_data)
    assert json.loads(decrypted) == test_data


@pytest.mark.asyncio
async def test_get_api_key(mock_redis) -> None:
    """Test retrieving and decrypting an API key from Redis."""
    test_data = {"username": "test_user", "role": "user"}
    json_data = json.dumps(test_data)
    encrypted_data = crypto.encrypt_data(json_data)

    prefixed_key = redis_key_store.api_key_prefix("test-key")
    mock_redis.data[prefixed_key] = encrypted_data

    result = await redis_key_store.get_api_key("test-key")

    assert result == test_data


@pytest.mark.asyncio
async def test_get_api_key_nonexistent(mock_redis) -> None:
    """Test retrieving a non-existent API key."""
    result = await redis_key_store.get_api_key("nonexistent-key")
    assert result is None


@pytest.mark.asyncio
async def test_get_api_key_invalid_data(mock_redis) -> None:
    """Test retrieving an API key with invalid/corrupted data."""
    prefixed_key = redis_key_store.api_key_prefix("invalid-key")
    mock_redis.data[prefixed_key] = "This is not encrypted data"

    result = await redis_key_store.get_api_key("invalid-key")
    assert result is None


@pytest.mark.asyncio
async def test_delete_api_key(mock_redis) -> None:
    """Test deleting an API key from Redis."""
    test_data = {"username": "test_user", "role": "user"}
    await redis_key_store.set_api_key("test-key", test_data, ex=3600)

    prefixed_key = redis_key_store.api_key_prefix("test-key")
    assert prefixed_key in mock_redis.data

    await redis_key_store.delete_api_key("test-key")

    assert prefixed_key not in mock_redis.data


@pytest.mark.asyncio
async def test_set_key_exp(mock_redis) -> None:
    """Test setting the expiration for an API key."""
    test_data = {"username": "test_user", "role": "user"}
    await redis_key_store.set_api_key("test-key", test_data, ex=None)

    prefixed_key = redis_key_store.api_key_prefix("test-key")
    assert prefixed_key not in mock_redis.expirations

    await redis_key_store.set_key_exp("test-key", 7200)

    assert mock_redis.expirations[prefixed_key] == 7200


@pytest.mark.asyncio
async def test_error_handling_in_get_api_key(mock_redis) -> None:
    """Test error handling during API key retrieval."""
    prefixed_key = redis_key_store.api_key_prefix("corrupted-key")
    mock_redis.data[prefixed_key] = "Corrupted data"

    with patch("app.extensions.security.crypto.decrypt_data",
               side_effect=Exception("Decryption failed")):
        result = await redis_key_store.get_api_key("corrupted-key")
        assert result is None

    with patch("app.extensions.security.crypto.decrypt_data",
               return_value="Not valid JSON"):
        result = await redis_key_store.get_api_key("corrupted-key")
        assert result is None


@pytest.mark.asyncio
async def test_print_statements_in_key_store(mock_redis, capsys) -> None:
    """Test that print statements in the key store function correctly."""
    await redis_key_store.set_api_key("print-test", {"test": "data"}, ex=3600)

    await redis_key_store.get_api_key("print-test")

    captured = capsys.readouterr()
    assert "key set:" in captured.out
    assert "key get:" in captured.out
    assert "api_key:print-test" in captured.out
