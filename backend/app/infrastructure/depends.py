from typing import Annotated, Protocol

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import get_session
from .redis import get_redis_client

DatabaseDepends = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated[aioredis.Redis, Depends(get_redis_client)]


class AsyncSessionDependant(Protocol):
    def __init__(self, db: AsyncSession) -> None: ...


def db_depends_factory(dependant: type[AsyncSessionDependant]):
    async def db_depends(
        db: AsyncSession = Depends(get_session),
    ) -> AsyncSessionDependant:
        return dependant(db)

    return db_depends


class RedisDependant(Protocol):
    def __init__(self, redis: aioredis.Redis) -> None: ...


def redis_depends_factory(dependant: type[RedisDependant]):
    async def redis_depends(
        redis: aioredis.Redis = Depends(get_redis_client),
    ) -> RedisDependant:
        return dependant(redis)

    return redis_depends
