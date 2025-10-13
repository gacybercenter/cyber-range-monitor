"""
The shared dependencies across the entire application.

"""

from typing import Annotated, cast

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.infra.adapters import APITenant
from range_monitor.infra.security import CryptoService
from range_monitor.lifespan import APIContext


async def get_resources(request: Request) -> APIContext:
    # note: this isn't the actual type it's just to avoid other type errors
    return cast(APIContext, request.state)


ContextRequired = Annotated[APIContext, Depends(get_resources)]


async def get_redis_client(context: ContextRequired) -> Redis:
    return context.redis_db.get_client()


async def get_db_session(context: ContextRequired):
    async with context.db.session() as session:
        yield session


async def get_readonly_db_session(context: ContextRequired):
    async with context.db.readonly_session() as session:
        yield session


RedisDep = Annotated[Redis, Depends(get_redis_client)]
DatabaseDep = Annotated[AsyncSession, Depends(get_db_session)]
ReadonlyDatabaseDep = Annotated[AsyncSession, Depends(get_readonly_db_session)]


async def get_crypto_service(context: ContextRequired) -> CryptoService:
    return CryptoService(context.crypto_policy)


CryptoServiceDep = Annotated[CryptoService, Depends(get_crypto_service)]


class HttpTenantDepends:
    def __init__(self, name: str) -> None:
        self.name: str = name

    async def __call__(self, context: ContextRequired) -> APITenant:
        return context.api_tenants.get_tenant(self.name)


GuacTenantRequired = HttpTenantDepends('guacamole')
SaltstackTenantRequired = HttpTenantDepends('saltstack')
