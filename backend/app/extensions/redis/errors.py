

class RedisError(Exception):
    """Base class for Redis-related errors."""
    pass

class RedisConnectionError(RedisError):    
    def __init__(self, message: str = "Failed to connect to Redis.") -> None:
        super().__init__(f'RedisConnectionError: {message}')

class RedisNotConnectedError(RedisError):
    def __init__(self) -> None:
        details = 'Redis was never not connected or the connection failed. Call open_conn() first.'
        super().__init__(f'RedisNotConnectedError: {details}')

class RedisClientError(RedisError):
    def __init__(self, message: str = "An error occurred while using the Redis client.") -> None:
        super().__init__(f'RedisClientError: {message}')