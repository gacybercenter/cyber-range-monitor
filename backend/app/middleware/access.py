import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.adapters import log
from app.utils import request_parse


def _access_message(
    request: Request,
    request_id: str,
    ip: str,
    user_agent: str | None,
) -> str:
    return (
        f'{request_id} | <IP={ip}, User-Agent={user_agent}>'
        f'Incoming {request.method} request to {request.url}'
    )

def _response_message(
    response: Response,
    request_id: str,
    elapsed: float,
) -> str:
    return (
        f'The API responsed to request {request_id} in '
        f'{elapsed:.3f}s with a HTTP '
        f'{response.status_code} to the client.'
    )

class AccessMiddleware(BaseHTTPMiddleware):
    """
    Logs incoming requests and responses.

    Side effects
        - Adds a `fingerprint` attribute to `request.state`
        - On class instantiation, registers a logger in the JSON log registry.
    """
    _LOGGER_NAME: str = 'access'

    def __init__(
        self,
        app: ASGIApp,
        *,
        correlation_id_header: str,
        ip_header: str = 'X-Forwarded-For',
    ) -> None:
        super().__init__(app)
        self.ip_header: str = ip_header
        self.correlation_id_header: str = correlation_id_header
        log.get_json_adapter().register(
            name=self._LOGGER_NAME,
            level='INFO',
        )

    @property
    def logger(self):
        return log.get_json_adapter().get_logger(self._LOGGER_NAME)

    def _get_request_id(self, request: Request) -> str:
        """
        Extracts the request ID from the request headers.
        If not found, returns 'unknown'.
        """
        return request.headers.get(self.correlation_id_header, 'unknown')

    def _attach_req_state(self, request: Request) -> None:
        """
        Attaches a fingerprint to the request state for logging purposes.
        """
        request.state.ip_address = request_parse.get_request_ip(
            request,
            request_header=self.ip_header,
        )
        request.state.user_agent = request_parse.get_user_agent(request)


    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]]
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
        self._attach_req_state(request)
        response_time = time.perf_counter()
        logged = {
            'method': request.method,
            'url': str(request.url),
            'headers': dict(request.headers),
            'request_id': self._get_request_id(request),
            'ip_address': request.state.ip_address,
            'user_agent': request.state.user_agent,
        }

        if hasattr(request, 'body'):
            logged['body'] = await request.body()

        self.logger.info(
            _access_message(
                request,
                request_id=logged['request_id'],
                ip=logged['ip_address'],
                user_agent=logged['user_agent'],
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

        self.logger.info(
            _response_message(
                response,
                request_id=self._get_request_id(request),
                elapsed=response_time,
            ),
            **response_log,
        )

        return response
