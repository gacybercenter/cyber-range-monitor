from fastapi import FastAPI, Request
from time import time

from api.core.logging import LogWriter
from api.db.main import get_session
from typing import Any


logger = LogWriter('REQUESTS')

def register_request_logging(app: FastAPI) -> None:

    @app.middleware("http")
    async def log_requests(request: Request, call_next) -> Any:
        req_start = time()

        forwarded_for = request.headers.get("X-Forwarded-For")
        ip = request.client.host if request.client else "unknown"
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        
        
        async with get_session() as session:
            await logger.info(
                f'Inbound request... CLIENT(ip={ip}, method={request.method}, path={request.url.path})', 
                session
            )
            await session.close()
        response = await call_next(request)
        duration = f"{(time() - req_start):.3f}"  # seconds with 3 decimal places
        
        
        async with get_session() as session:
            await logger.info(
                f'The server responded with a ({response.status_code}) in ({duration}s) to the client', 
                session
            )
        
        return response
        
