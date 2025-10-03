from __future__ import annotations

import contextlib
import logging
import socket
import ssl
from collections.abc import Awaitable, Callable
from typing import Generic, TypeVar

import httpx

logger = logging.getLogger(__name__)

RequestHook = Callable[[httpx.Request], Awaitable[None]]
ResponseHook = Callable[[httpx.Response], Awaitable[None]]


def _hardened_ssl_context(
    ca_path: str | None = None,
) -> ssl.SSLContext:
    '''
    Creates SSL context for secure HTTP connections.
    - Attempts to negotiate HTTP/2 via ALPN, or falls back to HTTP/1.1.
    - Enforces TLS v1.2+ and disables insecure options.

    Parameters
    ----------
    ca_path : str | None, optional
        a path to a certificate authority, by default None

    Returns
    -------
    ssl.SSLContext
    '''
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_path)
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    ctx.options |= ssl.OP_NO_COMPRESSION
    if hasattr(ssl, "OP_NO_TICKET"):
        ctx.options |= ssl.OP_NO_TICKET

    with contextlib.suppress(ssl.SSLError):
        ctx.set_alpn_protocols(['h2', 'http/1.1'])

    return ctx


class _ClientTransport(httpx.AsyncBaseTransport):
    '''
    A custom HTTP transport that enforces secure connections
    '''
    SOCKET_OPTIONS = [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60),
        (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
        (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5),
    ]

    def __init__(self, *, ssl: ssl.SSLContext | None = None, http2: bool = True) -> None:
        self._inner = httpx.AsyncHTTPTransport(
            verify=ssl or _hardened_ssl_context(),
            http2=http2,
            socket_options=self.SOCKET_OPTIONS,
        )

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await self._inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self._inner.aclose()


T = TypeVar('T')


class ContextRequestHook(Generic[T]):
    _EXTENSION_KEY = '__RANGE_MONITOR_CTX__'

    def __init__(self, context: T) -> None:
        self._context = context

    async def __call__(self, request: httpx.Request) -> None:
        if self._EXTENSION_KEY not in request.extensions:
            request.extensions[self._EXTENSION_KEY] = self._context


async def log_client_request(request: httpx.Request) -> None:
    logger.info(
        'External HTTP Client Request [%s]:  %s',
        request.method,
        request.url
    )


async def log_client_response(response: httpx.Response) -> None:
    context = response.request.extensions.get(ContextRequestHook._EXTENSION_KEY)
    logger.info(
        'External HTTP Client Response [%s]: %s %s - %s',
        context,
        response.request.method,
        response.request.url,
        response.status_code
    )


class URLSchemeNotSupported(Exception):
    ...


async def verify_client_url(request: httpx.Request) -> None:

    if request.url.scheme == 'http':
        request.url = request.url.copy_with(scheme='https')

    if request.url.scheme != 'https':
        raise URLSchemeNotSupported(
            f'Only HTTPS scheme is supported, got: {request.url.scheme}'
        )

    try:
        host = request.url.host.encode('idna').decode('ascii')
    except UnicodeError:
        host = request.url.host or ''

    request.url = request.url.copy_with(host=host)


def create_client(
    base_url: str | httpx.URL,
    *,
    defaults: dict,
    transport: httpx.AsyncBaseTransport | None = None,
    headers: dict[str, str] | None = None,
    auth: httpx.Auth | None = None,
    request_hooks: list[RequestHook] | None = None,
    response_hooks: list[ResponseHook] | None = None,
) -> httpx.AsyncClient:
    '''
    Creates a configured HTTPX async client with secure transport,

    Parameters
    ----------
    base_url : str
    options : HttpxConfig
    transport : httpx.AsyncBaseTransport | None, optional
    headers : dict[str, str] | None, optional
    auth : httpx.Auth | None, optional
    request_hooks : list[RequestHook] | None, optional
    response_hooks : list[ResponseHook] | None, optional

    Returns
    -------
    httpx.AsyncClient
    '''
    transport = transport or _ClientTransport(http2=defaults.get('http2', True))
    return httpx.AsyncClient(
        **defaults,
        transport=transport,
        base_url=base_url,
        headers=headers or {},
        event_hooks={
            'request': request_hooks or [],
            'response': response_hooks or [],
        },
        auth=auth,
    )
