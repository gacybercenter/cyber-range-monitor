from __future__ import annotations

from typing import Annotated, Protocol

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from monitor_api.adapters import db, redis_client

from .auth.repo import SessionRepo
from .users.repo import RoleRepo, UserRepo

DatabaseDep = Annotated[AsyncSession, Depends(db.get_db)]

class DatabaseDependant(Protocol):
    def __init__(self, session: AsyncSession) -> None: ...

class RedisDependant(Protocol):
    def __init__(self, redis: aioredis.Redis) -> None: ...


def make_db_dep(adapter: type[DatabaseDependant]):
    """
    Factory function to create a database dependency for a given adapter.
    """
    async def _get_sql_adapter(db: DatabaseDep) -> DatabaseDependant:
        return adapter(db)

    return _get_sql_adapter

RedisDep = Annotated[aioredis.Redis, Depends(redis_client.get_redis_client)]

def make_redis_dep(adapter: type[RedisDependant]):
    """
    Factory function to create a Redis dependency for a given adapter.
    """
    async def _get_redis_adapter(redis: RedisDep) -> RedisDependant:
        return adapter(redis)

    return _get_redis_adapter


get_session_repo = make_redis_dep(SessionRepo)
SessionRepoDep = Annotated[SessionRepo, Depends(get_session_repo)]


get_user_repo = make_db_dep(UserRepo)
get_role_repo = make_db_dep(RoleRepo)

UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
RoleRepoDep = Annotated[RoleRepo, Depends(get_role_repo)]

