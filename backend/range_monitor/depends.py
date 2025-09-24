"""
The shared dependencies across the entire application.

"""
from typing import Annotated, cast

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.lifespan import SecurityPolicy, ServerResources


async def get_resources(request: Request) -> ServerResources:
    # note: this isn't the actual type it's just to avoid other type errors
    return cast(ServerResources, request.state)

ResourcesDep = Annotated[ServerResources, Depends(get_resources)]

async def get_security_policy(resources: ResourcesDep) -> SecurityPolicy:
    return resources.security_policy


async def get_redis(resources: ResourcesDep) -> Redis:
    return resources.redis_client

async def get_db(resources: ResourcesDep):
    async with resources.sql.session() as session:
        yield session


async def get_readonly_db(resources: ResourcesDep):
    async with resources.sql.readonly_session() as session:
        yield session

RedisDep = Annotated[Redis, Depends(get_redis)]
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
ReadonlyDatabaseDep = Annotated[AsyncSession, Depends(get_readonly_db)]
SecurityPolicyDep = Annotated[SecurityPolicy, Depends(get_security_policy)]
