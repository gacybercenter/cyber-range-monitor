from typing import Annotated, Protocol

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .db import DatabaseEngine
from .redis import RedisConnection

DatabaseDepends = Annotated[AsyncSession, Depends(DatabaseEngine.get_session)]
RedisDep = Annotated[aioredis.Redis, Depends(RedisConnection.get_connection)]


class AsyncSessionDependant(Protocol):
    def __init__(self, db: AsyncSession) -> None: ...


def db_depends_factory(dependant: type[AsyncSessionDependant]):
    async def db_depends(db: DatabaseDepends) -> AsyncSessionDependant:
        return dependant(db)

    return db_depends


class RedisDependant(Protocol):
    def __init__(self, redis: aioredis.Redis) -> None: ...


def redis_depends_factory(dependant: type[RedisDependant]):
    async def redis_depends(redis: RedisDep) -> RedisDependant:
        return dependant(redis)

    return redis_depends
