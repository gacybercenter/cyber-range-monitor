from typing import Any
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import re

from app.extensions.redis.connection import RedisConnection
from app.extensions.redis.client import RedisClient, sanitize_key
from app.extensions.redis.errors import RedisNotConnectedError, RedisConnectionError


CONNECTION_MODULE = 'app.extensions.redis.connection.RedisConnection'

@pytest.mark.asyncio
class TestAPIRedis:
    @pytest_asyncio.fixture
    async def mock_redis_connection(self) -> Any:
        """Fixture to mock the RedisConnection class"""
        with patch(CONNECTION_MODULE) as mock_conn:
            mock_redis = AsyncMock()

            mock_conn.is_alive = AsyncMock(return_value=True)

            mock_conn._conn = mock_redis
            mock_conn._instance = MagicMock()

            mock_conn.client.return_value.__aenter__.return_value = mock_redis

            yield mock_conn, mock_redis

    @pytest_asyncio.fixture
    async def redis_client(self) -> RedisClient:
        """Fixture to create a RedisClient instance"""
        return RedisClient()

    @pytest_asyncio.fixture
    def prefixed_redis_client(self) -> RedisClient:
        """Fixture to create a RedisClient instance with a prefix"""
        return RedisClient(key_prefix="test")

    @pytest.mark.parametrize(
        "input_key,expected_output",
        [
            ("normal_key", "normal_key"),
            ("key-with-dash", "key-with-dash"),
            ("key:with:colon", "key:with:colon"),
            ("key with spaces", "keywithspaces"),
            ("key!@#$%^&*()", "key"),
            ("eval_command", "safe_eval_command"),
            ("EXEC_function", "safe_EXEC_function"),
            ("flushall_db", "safe_flushall_db"),
            ("flushdb_now", "safe_flushdb_now"),
            ("keys_pattern", "safe_keys_pattern"),
        ]
    )
    def test_sanitize_key(self, input_key: str, expected_output: str) -> None:
        """Test that sanitize_key properly sanitizes keys"""
        result = sanitize_key(input_key)
        assert result == expected_output
        assert re.match(r'^[a-zA-Z0-9_\-:]+$', result)

    async def test_keyify_without_prefix(self, redis_client: RedisClient) -> None:
        """Test _keyify method without a prefix"""
        assert redis_client._keyify("test_key") == "test_key"
        assert redis_client._keyify("eval_test") == "safe_eval_test"
        assert redis_client._keyify("test@key") == "testkey"

    async def test_keyify_with_prefix(self, prefixed_redis_client: RedisClient) -> None:
        """Test _keyify method with a prefix"""
        assert prefixed_redis_client._keyify("test_key") == "test:test_key"
        assert prefixed_redis_client._keyify(
            "eval_test") == "test:safe_eval_test"
        assert prefixed_redis_client._keyify("test@key") == "test:testkey"

    async def test_set(self, mock_redis_connection, redis_client: RedisClient) -> None:
        """Test set method"""
        _, mock_redis = mock_redis_connection

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            await redis_client.set("test_key", "test_value")
            mock_redis.set.assert_called_once_with(
                "test_key", "test_value", ex=None)

    async def test_set_with_expiration(self, mock_redis_connection, redis_client) -> None:
        """Test set method with expiration"""
        _, mock_redis = mock_redis_connection

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            await redis_client.set("test_key", "test_value", ex=60)
            mock_redis.set.assert_called_once_with(
                "test_key", "test_value", ex=60)

    async def test_set_with_prefix(self, mock_redis_connection, prefixed_redis_client) -> None:
        """Test set method with key prefix"""
        _, mock_redis = mock_redis_connection

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            await prefixed_redis_client.set("test_key", "test_value")
            mock_redis.set.assert_called_once_with(
                "test:test_key", "test_value", ex=None)

    async def test_get(self, mock_redis_connection, redis_client) -> None:
        """Test get method"""
        _, mock_redis = mock_redis_connection
        mock_redis.get.return_value = "test_value"

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            value = await redis_client.get("test_key")
            mock_redis.get.assert_called_once_with("test_key")
            assert value == "test_value"

    async def test_get_with_prefix(self, mock_redis_connection, prefixed_redis_client) -> None:
        """Test get method with key prefix"""
        _, mock_redis = mock_redis_connection
        mock_redis.get.return_value = "test_value"

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            value = await prefixed_redis_client.get("test_key")
            mock_redis.get.assert_called_once_with("test:test_key")
            assert value == "test_value"

    async def test_expire(self, mock_redis_connection, redis_client) -> None:
        """Test expire method"""
        _, mock_redis = mock_redis_connection

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            await redis_client.expire("test_key", 60)
            mock_redis.expire.assert_called_once_with("test_key", 60)

    async def test_delete(self, mock_redis_connection, redis_client) -> None:
        """Test delete method"""
        _, mock_redis = mock_redis_connection

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )):
            await redis_client.delete("test_key")
            mock_redis.delete.assert_called_once_with("test_key")

    async def test_redis_not_connected(self) -> None:
        """Test behavior when Redis is not connected"""
        with patch.object(RedisConnection, 'client') as mock_client:
            mock_client.side_effect = RedisNotConnectedError()
            client = RedisClient()

            with pytest.raises(RedisNotConnectedError):
                await client.get("test_key")

    async def test_redis_connection_error(self) -> None:
        """Test behavior when Redis connection fails"""
        with patch.object(RedisConnection, 'client') as mock_client:
            mock_client.side_effect = RedisConnectionError("Connection failed")
            client = RedisClient()

            with pytest.raises(RedisConnectionError):
                await client.get("test_key")

    async def test_integration_flow(self) -> None:
        """Test the entire flow of a Redis operation"""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "test_value"

        with patch.object(RedisConnection, 'client', return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_redis),
            __aexit__=AsyncMock(),
        )), patch.object(RedisConnection, 'is_alive', new_callable=AsyncMock, return_value=True):

            client = RedisClient(key_prefix="app")
            value = await client.get("user:1234")

            mock_redis.get.assert_called_once_with("app:user:1234")
            assert value == "test_value"
