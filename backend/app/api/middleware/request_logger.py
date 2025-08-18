import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.infrastructure.log import JSONLogContext
from app.infrastructure.security.fingerprint import RequestFingerprinter, RequestInfo


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests and responses.

    Side effects
        - Adds a `fingerprint` attribute to `request.state`
        - On class instantiation, registers a logger in the JSON log registry.
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        correlation_id_header: str,
        ip_header: str = 'X-Forwarded-For',
    ) -> None:
        super().__init__(app)
        self.logger_name: str = 'access'
        self.ip_header: str = ip_header
        self.correlation_id_header: str = correlation_id_header


    @property
    def access_logger(self):
        return JSONLogContext.get_logger(self.logger_name)

    def _access_message(
        self,
        request: Request,
        fingerprint: RequestInfo,
        id: str
    ) -> str:
        return (
            f'{id} | Incoming {request.method} request to '
            f'{request.url} from {fingerprint.ip} '
        )

    def _response_message(
        self,
        response: Response,
        request_id: str,
        elapsed: float,
    ) -> str:
        return (
            f'The API responsed to request {request_id} in '
            f'{elapsed:.3f}s with a HTTP '
            f'{response.status_code} to the client.'
        )

    def _get_request_id(self, request: Request) -> str:
        """
        Extracts the request ID from the request headers.
        If not found, returns 'unknown'.
        """
        return request.headers.get(self.correlation_id_header, 'unknown')

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """
        Logs incoming requests and outgoing responses with relevant details
        for monitoring and debugging.

        Side effects
            - Adds a `fingerprint` attribute to `request.state`

        Parameters
        ----------
        request : Request
        call_next : Callable[[Request], Awaitable[Response]]

        Returns
        -------
        Response
        """

        response_time = time.perf_counter()
        fingerprinter = RequestFingerprinter()
        request.state.fingerprint = await fingerprinter.get_fingerprint(
            request,
            ip_header=self.ip_header
        )

        logged = {
            'method': request.method,
            'url': str(request.url),
            'headers': dict(request.headers),
            'fingerprint': asdict(request.state.fingerprint),
            'request_id': self._get_request_id(request),
        }
        if hasattr(request, 'body'):
            logged['body'] = await request.body()

        self.access_logger.info(
            self._access_message(
                request,
                request.state.fingerprint,
                id=self._get_request_id(request),
            ),
            **logged,
        )

        response: Response = await call_next(request)
        response_time = time.perf_counter() - response_time

        response_log = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'elapsed': response_time,
            'okay': response.status_code < 400,
        }

        if hasattr(response, 'body'):
            response_log['body'] = response.body

        self.access_logger.info(
            self._response_message(
                response,
                request_id=self._get_request_id(request),
                elapsed=response_time,
            ),
            **response_log,
        )

        return response
