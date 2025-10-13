import asyncio
import dataclasses as dc
import logging
import uuid
from contextlib import asynccontextmanager
from typing import NamedTuple, Self

import httpx

from range_monitor.core import http
from range_monitor.infra.adapters import utils as tenant_utils
from range_monitor.infra.adapters._auth import APIAuthentication, AuthScheme
from range_monitor.infra.adapters.config import HttpxConfig

logger = logging.getLogger(__name__)


@dc.dataclass(frozen=True)
class HttpTenantConfig:
    name: str
    auth_scheme: type[AuthScheme]
    headers: dict[str, str] | None = None
    request_hooks: list[http.RequestHook] | None = None
    response_hooks: list[http.ResponseHook] | None = None


@dc.dataclass(frozen=True)
class TenantContext:
    """
    The context for a tenant connection, includes
    the unique datasource ID, any state parameters,

    """

    datasource_id: uuid.UUID
    state: dict[str, str] = dc.field(default_factory=dict)
    credentials: dict[str, str] = dc.field(default_factory=dict)

    def hash(self) -> bytes:
        return tenant_utils.hash_dataclass(self)  # type: ignore

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TenantContext):
            return NotImplemented

        return self.hash() == other.hash()


class _TenantConnection(NamedTuple):
    client: httpx.AsyncClient
    auth: APIAuthentication


def create_api_tenant(
    base_url: httpx.URL | str,
    tenant_config: HttpTenantConfig,
    context: TenantContext,
    http_config: HttpxConfig,
) -> _TenantConnection:
    """
    Creates an API tenant connection with the given configuration

    Parameters
    ----------
    base_url : httpx.URL | str
    tenant_config : HttpTenantConfig
    context : TenantContext
    http_config : HttpxConfig

    Returns
    -------
    _TenantConnection
    """
    auth_client = http.create_client(
        defaults=http_config.client_kwargs,
        base_url=base_url,
        headers=tenant_config.headers,
    )

    auth_provider = APIAuthentication(
        auth_client=auth_client,
        scheme=tenant_config.auth_scheme(),
        credentials=context.credentials,
    )
    api_client = http.create_client(
        base_url=base_url,
        defaults=http_config.client_kwargs,
        headers=tenant_config.headers,
        auth=auth_provider,
    )

    return _TenantConnection(client=api_client, auth=auth_provider)


class APITenant:
    """
    An API tenant that manages an HTTP client with a specific
    authentication scheme and is responsible for its lifecycle.
    """

    def __init__(self, config: HttpTenantConfig, http_config: HttpxConfig) -> None:
        self._config = config
        self._connection: _TenantConnection | None = None
        self._context: TenantContext | None = None
        self._lock: asyncio.Lock = asyncio.Lock()
        self._http_config: HttpxConfig = http_config

    async def __close(self) -> None:
        if self._connection:
            await self._connection.client.aclose()
            if self._connection.auth:
                await self._connection.auth.kill()

            self._connection = None
            self._context = None

    async def aconnect(
        self, base_url: str | httpx.URL, context: TenantContext
    ) -> httpx.AsyncClient:
        logger.info(
            f'Connecting to tenant {self._config.name}, {context.datasource_id}'
        )
        async with self._lock:
            if self._connection and self._context and self._context == context:
                logger.info('Reusing existing tenant connection.')
                return self._connection.client

            if self._connection:
                logger.info('Closing existing tenant connection...')
                await self.__close()

            self._connection = create_api_tenant(
                base_url=base_url,
                tenant_config=self._config,
                context=context,
                http_config=self._http_config,
            )

            self._context = context
            logger.info(
                f'Tenant {self._config.name}-{context.datasource_id} connection'
                'established.'
            )

        return self._connection.client

    async def adisconnect(self) -> None:
        logger.debug(f'Disconnecting from tenant {self._config.name}...')
        async with self._lock:
            await self.__close()

    def is_connected(self) -> bool:
        return self._connection is not None and self._context is not None

    def get_client(self) -> httpx.AsyncClient | None:
        if not self._connection:
            return None
        return self._connection.client

    def get_context(self) -> TenantContext | None:
        return self._context

    @asynccontextmanager
    async def auth_scheme(self, base_url: str | httpx.URL, context: TenantContext):
        connection = create_api_tenant(
            base_url=base_url,
            tenant_config=self._config,
            context=context,
            http_config=self._http_config,
        )

        try:
            yield connection.auth
        finally:
            await connection.client.aclose()
            await connection.auth.kill()

    async def authenticate(self) -> None:
        if not self._connection:
            logger.warning('No existing connection to authenticate, skipping...')
            return
        await self._connection.auth.authenticate()


@dc.dataclass(frozen=True)
class HttpTenantPool:
    """
    A pool of HTTP API tenants for managing multiple
    API clients with different authentication schemes
    responsible for their lifecycle.
    """

    options: HttpxConfig
    _tenants: dict[str, APITenant] = dc.field(default_factory=dict, init=False)

    @classmethod
    def create(cls, options: HttpxConfig, tenants: dict[str, HttpTenantConfig]) -> Self:
        this = cls(options=options)
        logger.info('Configuring HTTP tenants: %s', ', '.join(tenants.keys()))
        for name, config in tenants.items():
            this._tenants[name] = APITenant(config=config, http_config=options)

        return this

    def get_tenant(self, name: str) -> APITenant:
        if name not in self._tenants:
            raise KeyError(f'Tenant `{name}` is not configured.')
        return self._tenants[name]

    @property
    def names(self) -> list[str]:
        return list(self._tenants.keys())

    async def aclose(self) -> None:
        for tenant in self._tenants.values():
            await tenant.adisconnect()
        self._tenants.clear()
