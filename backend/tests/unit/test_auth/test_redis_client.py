from typing import Any
import pytest
from unittest.mock import patch, AsyncMock

import redis
import redis.exceptions

from app.extensions import redis_client


@pytest.mark.asyncio
async def test_sanitize() -> None:
    """Test Redis key sanitization function."""
    # Test normal keys
    normal_failed = 'Normal key failed after sanitization'
    assert redis_client.sanitize("user:123") == "user:123", normal_failed
    assert redis_client.sanitize("api_key:abc") == "api_key:abc", normal_failed
    assert redis_client.sanitize(
        "session-12345") == "session-12345", normal_failed

    # Test keys with special characters
    special_char = 'Special characters were not santizied before storage'
    assert redis_client.sanitize("user;123") == "user123", special_char
    assert redis_client.sanitize("api_key/abc") == "api_keyabc", special_char
    assert redis_client.sanitize(
        "session*12345") == "session12345", special_char

    assert redis_client.sanitize(
        "user' OR 1=1;") == "userOR11", 'SQL injection not sanitized'

    # Test keys with commands that should be prefixed
    cmd_worked = 'Command not sanitized'
    assert redis_client.sanitize("eval('return 1')") == "safe_evalreturn1", cmd_worked
    assert redis_client.sanitize("FLUSHALL") == "safe_FLUSHALL", cmd_worked
    assert redis_client.sanitize("keys *") == "safe_keys", cmd_worked


@pytest.mark.asyncio
async def test_set_and_get_key(mock_redis) -> None:
    """Test setting and getting a key in Redis."""
    await redis_client.set_key("test:key", "test-value", ex=3600)

    assert mock_redis.data["test:key"] == "test-value", "Key not set correctly"
    assert mock_redis.expirations["test:key"] == 3600, "Key not set correctly"

    result = await redis_client.get_key("test:key")
    assert result == "test-value", "Key retrieved with a different value" 
    
    result = await redis_client.get_key("nonexistent:key")
    assert result is None, 'Non-existent key should return None'


@pytest.mark.asyncio
async def test_delete_key(mock_redis) -> None:
    """Test deleting a key from Redis."""
    await redis_client.set_key("test:delete", "value-to-delete", ex=3600)
    assert mock_redis.data["test:delete"] == "value-to-delete", "Key not set correctly"

    await redis_client.delete_key("test:delete")
    assert "test:delete" not in mock_redis.data, "Key not deleted correctly"
    assert "test:delete" not in mock_redis.expirations, "Key not deleted correctly"


@pytest.mark.asyncio
async def test_set_expiration(mock_redis) -> Any:
    """Test setting the expiration time for a key."""
    await redis_client.set_key("test:expire", "value", ex=None)
    assert "test:expire" not in mock_redis.expirations

    await redis_client.set_expiration("test:expire", 1800)

    assert mock_redis.expirations["test:expire"] == 1800

    await redis_client.set_expiration("nonexistent:key", 1800)
    assert "nonexistent:key" not in mock_redis.expirations


@pytest.mark.asyncio
async def test_key_prefixing_in_get_and_set(mock_redis) -> Any:
    """Test that keys are properly sanitized in get and set operations."""
    await redis_client.set_key("user;123", "test-value", ex=3600)

    assert "user;123" not in mock_redis.data, "Key not sanitized before storage"
    assert "user123" in mock_redis.data, "Key not sanitized before storage"

    result = await redis_client.get_key("user;123")
    assert result == "test-value", "Key retrieval failed to sanitize key"


@pytest.mark.asyncio
async def test_redis_client_with_async_await(monkeypatch) -> Any:
    """Test that the Redis client correctly handles both synchronous and asynchronous responses."""
    sync_mock = "sync-value"
    async_mock = AsyncMock(return_value="async-value")

    monkeypatch.setattr(
        "app.extensions.redis_client.redis_client.get", 
        lambda *args, **kwargs: sync_mock
    )
    result = await redis_client.get_key("sync:key")
    assert result == "sync-value", "Sync key retrieval failed"

    monkeypatch.setattr("app.extensions.redis_client.redis_client.get",
        lambda *args, **kwargs: async_mock())
    result = await redis_client.get_key("async:key")
    assert result == "async-value", "Async key retrieval failed"
    async_mock.assert_called_once()


@pytest.mark.asyncio
async def test_redis_connection_error_handling() -> None:
    """Test handling of Redis connection errors."""
    error_redis = AsyncMock()
    error_redis.get.side_effect = redis.exceptions.ConnectionError(
        "Connection refused")

    with patch("app.extensions.redis_client.redis_client", error_redis):
        with pytest.raises(redis.exceptions.ConnectionError):
            await redis_client.get_key("any:key")
