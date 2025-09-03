



import asyncio
import contextlib
import dataclasses

import httpx


def _defaulthttpxtimeout() -> httpx.Timeout:
    return httpx.Timeout(
        connect=5.0,
        read=10.0,
        write=10.0,
        pool=10.0,
    )

def _defaulthttpxlimits() -> httpx.Limits:
    return httpx.Limits(
        max_keepalive_connections=5,
        max_connections=20,
        keepalive_expiry=30.0,
    )

def _defaulthttpxtransport() -> httpx.AsyncHTTPTransport:
    return httpx.AsyncHTTPTransport(http2=True)

@dataclasses.dataclass(slots=True)
class HttpClientOptions:
    '''
    The options for configuring an `httpx.AsyncClient` instance
    with safe defaults.
    '''
    base_url: str = ''
    headers: dict[str, str] | None = None
    timeout: httpx.Timeout = dataclasses.field(
        default_factory=_defaulthttpxtimeout
    )
    limits: httpx.Limits = dataclasses.field(
        default_factory=_defaulthttpxlimits
    )
    transport: httpx.AsyncHTTPTransport = dataclasses.field(
        default_factory=_defaulthttpxtransport
    )
    auth: httpx.Auth | None = None




@dataclasses.dataclass(slots=True)
class HttpClientManager:
    '''
    A manager for `httpx.AsyncClient` instances which allows for caching of client
    instances and lifespan management.
    '''
    _cache: dict[str, httpx.AsyncClient] = dataclasses.field(
        default_factory=dict,
        init=False
    )
    _locks: dict[str, asyncio.Lock] = dataclasses.field(
        default_factory=dict,
        init=False
    )

    @contextlib.asynccontextmanager
    async def _clientlock(self, client_id: str):
        '''
        An async context manager that provides a lock for a given client ID.
        '''
        if client_id not in self._locks:
            self._locks[client_id] = asyncio.Lock()
        async with self._locks[client_id]:
            yield

    def _makeclient(self, options: HttpClientOptions | None) -> httpx.AsyncClient:
        options = options or HttpClientOptions()

        return httpx.AsyncClient(
            base_url=options.base_url.rstrip('/'),
            headers=options.headers or {"Content-Type": "application/json"},
            timeout=options.timeout,
            limits=options.limits,
            auth=options.auth,
            transport=options.transport,
        )

    async def get(
        self,
        client_id: str,
        *,
        options: HttpClientOptions | None = None
    ) -> httpx.AsyncClient:
        '''
        Gets or creates an `httpx.AsyncClient` instance.

        Parameters
        ----------
        client_id : str
        options : HttpClientOptions | None, optional
            _The options for the the client_, by default None

        Returns
        -------
        httpx.AsyncClient
            _The async client_
        '''
        async with self._clientlock(client_id):
            client = self._cache.get(client_id)
            if client:
                return client
            client = self._makeclient(options)
            self._cache[client_id] = client
            return client


    async def invalidate(self, client_id: str) -> None:
        '''
        removes and closes the client associated with the given client ID.
        '''
        client = self._cache.pop(client_id, None)
        if client:
            await client.aclose()
        self._locks.pop(client_id, None)

    async def aclose(self) -> None:
        '''
        Closes all cached clients and clears the cache.
        '''
        for client in self._cache.values():
            await client.aclose()
        self._cache.clear()
        self._locks.clear()