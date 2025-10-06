from __future__ import annotations

import logging
from dataclasses import dataclass

from range_monitor.config import AppSettings
from range_monitor.infra.adapters import (
    HttpTenantConfig,
    HttpTenantPool,
    OpenstackTenant,
)
from range_monitor.infra.db import SqliteDatabase
from range_monitor.infra.redis import RedisDatabase
from range_monitor.infra.security import (
    CryptoPolicy,
    JwtPolicy,
    create_crypto_policy,
    create_jwt_policy,
)
from range_monitor.sources.auth_schemes import GuacamoleAuth, SaltstackAuthToken

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class APIContext:
    '''
    The resources that are shared via the lifespan context manager,
    not an actual type hint inside of the depenedencies
    '''
    redis_db: RedisDatabase
    db: SqliteDatabase
    jwt_policy: JwtPolicy
    crypto_policy: CryptoPolicy
    api_tenants: HttpTenantPool
    openstack_tenant: OpenstackTenant

    def share(self) -> dict:
        return {
            'redis_db': self.redis_db,
            'db': self.db,
            'jwt_policy': self.jwt_policy,
            'crypto_policy': self.crypto_policy,
            'api_tenants': self.api_tenants,
            'openstack_tenant': self.openstack_tenant,
        }

    async def setup(self) -> None:
        await self.db.create_tables(self.crypto_policy)
        await self.redis_db.aconnect()

    async def dispose(self) -> None:
        if self.db:
            await self.db.disconnect()

        if self.redis_db:
            await self.redis_db.adisconnect()



def create_api_context(settings: AppSettings) -> APIContext:

    sql_db = SqliteDatabase.from_config(
        settings.sqlite,
        is_testing=settings.app.options.testing
    )
    redis_db = RedisDatabase.from_config(options=settings.redis)
    jwt_policy = create_jwt_policy(options=settings.jwt)
    crypto_policy = create_crypto_policy()

    tenant_headers = {
        'Accept': 'application/json',
        'User-Agent': 'RangeMonitor-API-Agent/1.0',
    }

    api_tenants = {
        'guacamole': HttpTenantConfig(
            name='guacamole',
            auth_scheme=GuacamoleAuth,
            headers=tenant_headers
        ),
        'saltstack': HttpTenantConfig(
            name='saltstack',
            auth_scheme=SaltstackAuthToken,
            headers=tenant_headers
        )
    }

    api_tenants = HttpTenantPool.create(settings.httpx, api_tenants)
    openstack_tenant = OpenstackTenant()

    return APIContext(
        redis_db=redis_db,
        db=sql_db,
        jwt_policy=jwt_policy,
        crypto_policy=crypto_policy,
        api_tenants=api_tenants,
        openstack_tenant=openstack_tenant,
    )


