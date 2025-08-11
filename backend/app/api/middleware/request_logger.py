import logging
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from app.common.types import CallNext
from app.core.security.schema import ClientFingerprint

logger = logging.getLogger("access")


async def request_logging_middleware(request: Request, call_next: CallNext) -> Response:
    """Logs the IPs of all requests sent to the API and the subsequent responses and the
    response time of each request

    Arguments:
        request {Request} -- the original request
        call_next {CallNext} -- the next middleware in the chain

    Returns:
        Response -- the response from the API
    """

    request_id = str(uuid.uuid4())
    request_fingerprint = await ClientFingerprint.create(request)

    response_time = time.perf_counter()
    logger.info(
        f"Inbound HTTP [bold blue]{request.method} Request[/bold blue]  @{request.url.path} from client -> "
        f"[bold]{request_fingerprint or 'could not determine'} "
        f"Request ID: {request_id or 'could not determine'})\n\n"
    )
    response: Response = await call_next(request)
    response_time = time.perf_counter() - response_time

    logger.info(
        f"The API responsed to request {request_id} in "
        f"{response_time:.3f}s with a HTTP "
        f"{response.status_code}to the client."
        f"\nRequest ID: {request_id or 'could not determine'})"
        f"\nClient fingerprint: {request_fingerprint or 'could not determine'}\n"
    )

    return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app=app, dispatch=request_logging_middleware)
