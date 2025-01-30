from fastapi import FastAPI, Request
from typing import Awaitable, Callable
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.requests import Request
from time import perf_counter

from app.common import LogWriter
from app.core.db import get_session
from typing import Any, Coroutine


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.logger = LogWriter('REQUESTS')        
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]):
        start = perf_counter()
        
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = request.client.host if request.client else "unknown"
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        
        async with get_session() as session:
            await self.logger.info(
                f'Inbound request... CLIENT(ip={ip}, method={request.method}, path={request.url.path})', 
                session
            )
            await session.close()
        
        response: Response = await call_next(request)
        req_duration = f"{(perf_counter() - start):.3f}"  # seconds with 3 decimal places
        
        async with get_session() as session:
            await self.logger.info(
                f'The server responded with a ({response.status_code}) in ({req_duration}s) to the client', 
                session
            )
            await session.close()
        return response
        
