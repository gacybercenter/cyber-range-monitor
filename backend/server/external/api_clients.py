from __future__ import annotations

import asyncio
import dataclasses as dc
import logging
from typing import TYPE_CHECKING, Final, Self

from server.external import http
from server.external.auth_flows import AuthFlow, ClientAuth

if TYPE_CHECKING:
    import uuid

    import httpx


logger = logging.getLogger(__name__)


@dc.dataclass(slots=True)
class ApiClientOptions:
    name: str
    auth: type[AuthFlow]
    headers: dict[str, str] | None = None


@dc.dataclass(frozen=True)
class ClientContext:
    '''
    The context for a tenant connection, includes
    the unique datasource ID, any state parameters,

    '''

    datasource_id: uuid.UUID
    state: dict[str, str] = dc.field(default_factory=dict)
    credentials: dict[str, str] = dc.field(default_factory=dict)

    def hash(self) -> bytes:
        '''
        Creates a hash of the context for comparison purposes.

        Returns
        -------
        bytes
        '''
        state_items = tuple(sorted(self.state.items()))
        credentials_items = tuple(sorted(self.credentials.items()))
        return (
            str(self.datasource_id).encode('utf-8')
            + str(state_items).encode('utf-8')
            + str(credentials_items).encode('utf-8')
        )


@dc.dataclass(slots=True)
class ClientConnection:
    client: httpx.AsyncClient
    auth: ClientAuth
    context: ClientContext

    @classmethod
    def begin(
        cls,
        base_url: str | httpx.URL,
        *,
        options: ApiClientOptions,
        context: ClientContext,
    ) -> Self:
        auth_client = http.create_async_client(
            base_url=base_url,
            headers=options.headers
        )
        auth = ClientAuth(
            auth_client=auth_client,
            auth_flow=options.auth(),
            credentials=context.credentials,
        )

        api_client = http.create_async_client(
            base_url=base_url,
            headers=options.headers,
            auth=auth,
        )
        return cls(client=api_client, auth=auth, context=context)

    async def aclose(self) -> None:
        logger.info(
            f'Closing connection for {self.context.datasource_id}'
            f', at {self.client.base_url}'
        )
        await self.client.aclose()
        await self.auth.kill()

    def is_same_context(self, context: ClientContext) -> bool:
        return self.context.hash() == context.hash()


class ApiClient:
    '''
    An API tenant that manages an HTTP client with a specific
    authentication scheme and is responsible for its lifecycle.
    '''

    def __init__(self, config: ApiClientOptions) -> None:
        self._config = config
        self._connection: ClientConnection | None = None
        self._lock: asyncio.Lock = asyncio.Lock()

    async def _close(self) -> None:
        '''
        Closes the existing connection if any, not thread-safe
        always close within a lock, do not stack multiple locks
        at once to prevent deadlocks.
        '''
        if self._connection:
            await self._connection.aclose()
            self._connection = None

    async def connect(
        self, base_url: str | httpx.URL, context: ClientContext
    ) -> httpx.AsyncClient:
        '''
        Connects to the API with the given context, reusing
        existing connections if the context matches. Use sparingly
        to avoid unnecessary connection churn.
        '''
        logger.info(f'Connecting to tenant {self._config.name}, {context.datasource_id}')
        async with self._lock:
            if self._connection and self._connection.is_same_context(context):
                logger.info('Reusing existing client connection.')
                return self._connection.client

            if self._connection:
                logger.info('Closing existing client connection...')
                await self._close()

            self._connection = ClientConnection.begin(
                base_url=base_url,
                options=self._config,
                context=context,
            )

            logger.info(
                f'Tenant {self._config.name}-{context.datasource_id} http connection'
                'established.'
            )

        return self._connection.client

    async def aclose(self) -> None:
        logger.debug(f'Disconnecting from tenant {self._config.name}...')
        async with self._lock:
            await self._close()

    def is_alive(self) -> bool:
        return self._connection is not None

    @property
    def connection(self) -> ClientConnection:
        if not self._connection:
            raise RuntimeError('No active connection found for the tenant.')
        return self._connection

    async def try_credentials(
        self, base_url: str | httpx.URL, context: ClientContext
    ) -> None:
        async with http.create_async_client(
            base_url=base_url,
            headers=self._config.headers
        ) as auth_client:
            auth = ClientAuth(
                auth_client=auth_client,
                auth_flow=self._config.auth(),
                credentials=context.credentials,
            )
            await auth.authenticate(credentials=context.credentials)

    async def authenticate(self) -> None:
        if not self._connection:
            logger.warning('No existing connection to authenticate, skipping...')
            return
        await self._connection.auth.authenticate()

    def get_client(self) -> httpx.AsyncClient | None:
        return None if not self._connection else self._connection.client


@dc.dataclass(slots=True)
class _ApiClientPool:
    '''
    A pool of HTTP API tenants for managing multiple
    API clients with different authentication schemes
    responsible for their lifecycle.
    '''

    _tenants: dict[str, ApiClient] = dc.field(default_factory=dict, init=False)

    def register(self, tenants: dict[str, ApiClientOptions]) -> None:
        '''
        Registers additional tenants to the pool at runtime.

        Parameters
        ----------
        tenants : dict[str, ApiClientOptions]
            The tenants to register.
        '''
        for name, config in tenants.items():
            logger.info(f'Registering tenant `{name}` to the client pool.')
            if name in self._tenants:
                raise KeyError(f'Tenant `{name}` is already registered.')

            self._tenants[name] = ApiClient(config=config)

    def get_client(self, name: str) -> ApiClient:
        if name not in self._tenants:
            raise KeyError(
                f'Tenant `{name}` was not added to the client pool at runtime.'
            )
        return self._tenants[name]

    @property
    def names(self) -> list[str]:
        return list(self._tenants.keys())

    async def adispose(self) -> None:
        for tenant in self._tenants.values():
            await tenant.aclose()
        self._tenants.clear()


api_client_pool: Final[_ApiClientPool] = _ApiClientPool()
