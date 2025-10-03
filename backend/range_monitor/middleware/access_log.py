from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from http import HTTPStatus

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from range_monitor.infra import log
from range_monitor.schema.headers import Device


class AccessMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self.logger = log.get_loguru()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.perf_counter()
        device = Device.from_request(request)

        message = f'[{request.method}] -> {request.url} {str(device)}'

        cor_id = request.headers.get('X-Request-ID', 'N/A')
        self.logger.log(
            'SECURITY',
            message,
            correlation_id=cor_id,
            method=request.method,
            url=str(request.url),
            path=request.url.path,
            ip_address=device.ip_address,
            user_agent=str(device.user_agent),
        )

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        phrase = HTTPStatus(response.status_code).phrase
        message = (
            f'Responded to {cor_id} in {duration:.3f}s with a '
            f'{response.status_code}, {phrase}.'
        )

        self.logger.log(
            'SECURITY',
            message,
            status_code=response.status_code,
            phrase=phrase,
            elapsed=duration,
            correlation_id=response.headers.get('X-Request-ID', 'N/A'),
        )

        return response
