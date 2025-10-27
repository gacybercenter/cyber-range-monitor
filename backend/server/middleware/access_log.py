from __future__ import annotations

import time
from http import HTTPStatus
from typing import TYPE_CHECKING

from starlette.middleware.base import BaseHTTPMiddleware

from server.headers import ClientInfo
from server.logger import get_loguru_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from fastapi import Request, Response
    from starlette.types import ASGIApp


class AccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = get_loguru_logger(__name__)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        client = ClientInfo.from_request(request)

        message = f'[{request.method}] -> {request.url} {client!s}'

        cor_id = request.headers.get('X-Request-ID', 'N/A')
        self.logger.info(
            message,
            correlation_id=cor_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            ip_address=client.ip_address,
            user_agent=str(client.user_agent),
        )

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        phrase = HTTPStatus(response.status_code).phrase
        message = (
            f'Responded to {cor_id} in {duration:.3f}s with a '
            f'{response.status_code}, {phrase}.'
        )

        self.logger.info(
            message,
            status_code=response.status_code,
            phrase=phrase,
            elapsed=duration,
            correlation_id=response.headers.get('X-Request-ID', 'N/A'),
        )

        return response
