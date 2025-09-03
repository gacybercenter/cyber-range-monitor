"""
The shared dependencies across the entire application.

"""
from typing import Annotated, cast

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.core.crypto import Encryptor, PasswordHashes, SignatureProvider
from range_monitor.http_clients import HttpClientManager
from range_monitor.lifespan import APIResources


async def get_resources(request: Request) -> APIResources:
    # note: this isn't the actual type it's just to avoid other type errors
    return cast(APIResources, request.state)


ResourcesDep = Annotated[APIResources, Depends(get_resources)]

async def get_db(resources: ResourcesDep):
    async with resources.db() as session:
        yield session

async def get_redis_client(resources: ResourcesDep) -> Redis:
    return resources.redis


async def get_passwords(resources: ResourcesDep) -> PasswordHashes:
    return resources.passwords

async def get_encryptor(resources: ResourcesDep) -> Encryptor:
    return resources.encryptor


async def get_signatures(resources: ResourcesDep) -> SignatureProvider:
    return resources.signatures

async def get_http_clients(resources: ResourcesDep) -> HttpClientManager:
    return resources.http_clients


DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]
PasswordsDep = Annotated[PasswordHashes, Depends(get_passwords)]
EncryptorDep = Annotated[Encryptor, Depends(get_encryptor)]
SignatureDep = Annotated[SignatureProvider, Depends(get_signatures)]