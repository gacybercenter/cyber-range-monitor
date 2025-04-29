import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response


from fastapi import Request

from starlette.responses import Response
from starlette.types import ASGIApp

from app.common.types import CallNext
from app.core.logs import get_security_logger




logger = get_security_logger()

async def request_logging_middleware(
    request: Request,
    call_next: CallNext
) -> Response:
    '''Logs the IPs of all requests sent to the API and the subsequent responses and the
    response time of each request

    Arguments:
        request {Request} -- the original request
        call_next {CallNext} -- the next middleware in the chain

    Returns:
        Response -- the response from the API
    '''
    request_id = str(uuid.uuid4())


    
    forwarded_for = request.headers.get("X-Forwarded-For")
    ip = request.client.host if request.client else "unknown"
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()

    response_time = time.perf_counter()
    logger.info(
        f'Inbound HTTP {request.method} Request @{request.url.path} from client {ip}'
        f' (request_id={request_id})'
    )
    response: Response = await call_next(request)
    response_time = time.perf_counter() - response_time

    logger.info(
        f'The API responsed to request {request_id} in '
        f'[italic]{response_time:.3f}s[/italic] with a HTTP '
        f'[bold]{response.status_code}[/bold] to the client.'
    )

    return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, dispatch=request_logging_middleware)

        
        
        
        