from __future__ import annotations

import contextlib
import logging
import socket
import ssl
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, override

import httpx

from server.settings import get_app_settings

if TYPE_CHECKING:
    from server.configs.toml import HttpxConfig

logger = logging.getLogger(__name__)

type RequestHook = Callable[[httpx.Request], Awaitable[None]]
type ResponseHook = Callable[[httpx.Response], Awaitable[None]]


def get_ssl_context(
    ca_path: str | None = None,
) -> ssl.SSLContext:
    """
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
    """
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=ca_path)
    ctx.check_hostname = True
    ctx.verify_mode = ssl.CERT_REQUIRED

    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3

    ctx.options |= ssl.OP_NO_COMPRESSION
    if hasattr(ssl, 'OP_NO_TICKET'):
        ctx.options |= ssl.OP_NO_TICKET

    with contextlib.suppress(ssl.SSLError):
        ctx.set_alpn_protocols(['h2', 'http/1.1'])

    return ctx


class ClientTransport(httpx.AsyncBaseTransport):
    """
    A custom HTTP transport that enforces secure connections
    """

    SOCKET_OPTIONS = [
        (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
        (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
        (socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60),
        (socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10),
        (socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5),
    ]

    def __init__(self, *, http2: bool = True) -> None:
        self._inner = httpx.AsyncHTTPTransport(
            verify=get_ssl_context(),
            http2=http2,
            socket_options=self.SOCKET_OPTIONS,
        )

    @override
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        return await self._inner.handle_async_request(request)

    @override
    async def aclose(self) -> None:
        await self._inner.aclose()


async def log_client_request(request: httpx.Request) -> None:  # noqa: RUF029
    logger.info('External HTTP Client Request [%s]:  %s', request.method, request.url)


async def log_client_response(response: httpx.Response) -> None:  # noqa: RUF029
    logger.info(
        'External HTTP Client Response %s %s - %s',
        response.request.method,
        response.request.url,
        response.status_code,
    )


class URLSchemeInvalidError(Exception): ...


async def verify_client_url(request: httpx.Request) -> None:  # noqa: RUF029
    """
    Ensures that the request URL uses HTTPS scheme.

    Parameters
    ----------
    request : httpx.Request
        The request to check

    Raises
    ------
    URLSchemeInvalidError
        The URL scheme is not HTTPS
    """
    if request.url.scheme == 'http':
        request.url = request.url.copy_with(scheme='https')

    if request.url.scheme != 'https':
        raise URLSchemeInvalidError(
            f'Only HTTPS scheme is supported, got: {request.url.scheme}'
        )

    try:
        host = request.url.host.encode('idna').decode('ascii')
    except UnicodeError:
        host = request.url.host or ''

    request.url = request.url.copy_with(host=host)


def create_async_client(
    base_url: str | httpx.URL,
    *,
    httpx_options: HttpxConfig | None = None,
    transport: httpx.AsyncBaseTransport | None = None,
    headers: dict[str, str] | None = None,
    auth: httpx.Auth | None = None,
) -> httpx.AsyncClient:
    """
    Creates a configured HTTPX async client with secure transport,

    Parameters
    ----------
    base_url : str
        The base URL for the client.
    httpx_options : HttpxConfig
        Default parameters for the HTTPX client, by default None
    transport : httpx.AsyncBaseTransport | None, optional
        Custom transport for the client shouldn't be
        specified outside of testing, by default None
    headers : dict[str, str] | None, optional
        Default headers for the client, by default None
    auth : httpx.Auth | None, optional
        Authentication for the client, by default None

    Returns
    -------
    httpx.AsyncClient
    """
    httpx_options = httpx_options or get_app_settings().httpx
    transport = transport or ClientTransport(http2=httpx_options.http2)
    return httpx.AsyncClient(
        **httpx_options.dump_httpx_opts(),
        transport=transport,
        base_url=base_url,
        headers=headers or {},
        event_hooks={
            'request': [
                log_client_request,
                verify_client_url,
            ],
            'response': [
                log_client_response,
            ],
        },
        auth=auth,
    )
