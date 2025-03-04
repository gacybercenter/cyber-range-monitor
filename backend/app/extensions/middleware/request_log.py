import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.db.main import get_session
from app.extensions import api_console


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        '''logs the request and the time it takes to respond to a request from the client 
        Returns:
            Response -- _description_
        '''
        
        start = time.perf_counter()

        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = request.client.host if request.client else "unknown"
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()

        async with get_session() as session:
            await api_console.info(
                f"Inbound request... CLIENT(ip={ip}, method={request.method}, path={request.url.path})",
                session,
            )
            await session.close()

        response: Response = await call_next(request)
        # seconds with 3 decimal places
        req_duration = f"{(time.perf_counter() - start):.3f}"

        async with get_session() as session:
            await api_console.info(
                f"The server responded with a ({response.status_code}) in "
                f"({req_duration}s) to the client",
                session
            )
            await session.close()
        return response
