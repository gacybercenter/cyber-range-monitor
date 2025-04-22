
from fastapi import status

from app.core.errors.http_errors import (
    HTTPExcDetails, ApiHTTPException, HTTPErrorLabel
)

class RedisError(Exception):
    """Base class for Redis-related errors."""
    pass

class InvalidRedisKeyPrefix(RedisError):
    def __init__(self, message: str = "Invalid Redis key prefix.") -> None:
        super().__init__(f'InvalidRedisKeyPrefix: {message}')


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
        

class InvalidRedisKey(ApiHTTPException):
    '''Raises a 406 error when the user provides an invalid redis key
    to prevent injection attacks.'''

    def __init__(self) -> None:
        super().__init__(
            status.HTTP_406_NOT_ACCEPTABLE,
            details=HTTPExcDetails(
                message='The user provided an invalid redis key which was rejected due to injection concerns.',
                error_label=HTTPErrorLabel.INVALID_DATA
            )
        )
