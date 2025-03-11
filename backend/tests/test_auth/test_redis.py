import pytest

@pytest.mark.asyncio
async def test_redis_client() -> None:
    from app.extensions import redis_client
    await redis_client.set_key(
        'foo',
        'bar',
        None
    )
    value = await redis_client.get_key('foo')
    assert value == 'bar', 'Redis client failed to set and get a key'
    
    await redis_client.delete_key('foo')
    assert await redis_client.get_key('foo') is None, 'Redis client failed to delete a key'
    
    bad_key = 'key\r\nPING\r\n'
    
    result = await redis_client.set_key(bad_key, 'value', None)
    assert result is False, 'Redis client failed to sanitize a key'