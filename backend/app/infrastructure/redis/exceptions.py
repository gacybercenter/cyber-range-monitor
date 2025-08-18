from app.core.exceptions import InfrastructureError


class BaseRedisError(InfrastructureError):
    def __init__(self, detail: str, *, exc: Exception | None = None) -> None:
        super().__init__(adapter='Redis', detail=detail, exc=exc)


class RedisPoolNotInitializedError(BaseRedisError):
    def __init__(self) -> None:
        super().__init__(detail='Redis connection pool has not been initialized.')


class RedisConnectionFailed(BaseRedisError):
    def __init__(self, reason: str, exc: Exception) -> None:
        super().__init__(
            detail=f'Redis connection failed: {reason}',
            exc=exc,
        )
