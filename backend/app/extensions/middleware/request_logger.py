import logging
import re
import time
from typing import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response




class RequestLoggingMiddleware(BaseHTTPMiddleware):
    '''custom middleware to log the request and response times'''

    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.request_logger = logging.getLogger("requests")

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """logs the request and the time it takes to respond to a request from the client
        Returns:
            Response -- the response from the intercepted request
        """

        start = time.perf_counter()

        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = request.client.host if request.client else "unknown"
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()

        self.request_logger.info(
            '[green] Inbound request...[/green] -'
            f'[italic] CLIENT(ip={ip}, method={request.method}, path={request.url.path}) url=({request.url}) [/italic]',
        )
        response: Response = await call_next(request)
        req_duration = f"{(time.perf_counter() - start):.2f}"

        self.request_logger.info(
            f"The server responded with a [bold]{response.status_code}[/bold] in "
            f"[italic]({req_duration}s)[/italic] to the client"
        )

        return response
