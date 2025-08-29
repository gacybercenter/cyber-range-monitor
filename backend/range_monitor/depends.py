"""
The shared dependencies across the entire application.

"""
from typing import Annotated, cast

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.core.crypto import Encryptor, PasswordHashes, SignatureProvider
from range_monitor.lifespan import LifespanResources


async def get_resources(request: Request) -> LifespanResources:
    return cast(LifespanResources, request.state)


ResourcesDep = Annotated[LifespanResources, Depends(get_resources)]

async def get_db(resources: ResourcesDep):
    async with resources.db() as session:  # type: ignore
        yield session

async def get_redis_client(resources: ResourcesDep) -> Redis:
    return resources.redis  # type: ignore[return-value]


async def get_passwords(resources: ResourcesDep) -> PasswordHashes:
    return resources.passwords # type: ignore[return-value]

async def get_encryptor(resources: ResourcesDep) -> Encryptor:
    return resources.encryptor  # type: ignore[return-value]


async def get_signatures(resources: ResourcesDep) -> SignatureProvider:
    return resources.signatures  # type: ignore[return-value]


DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[Redis, Depends(get_redis_client)]
PasswordsDep = Annotated[PasswordHashes, Depends(get_passwords)]
EncryptorDep = Annotated[Encryptor, Depends(get_encryptor)]
SignatureDep = Annotated[SignatureProvider, Depends(get_signatures)]