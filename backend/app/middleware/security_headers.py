from fastapi import FastAPI
from fastapi import Request, Response

from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware

from .type import CallNext
from .options import SecurityHeaderOptions


class SecurityHeaderMiddleware(BaseHTTPMiddleware):
    '''wraps responses returned by the API with security headers 

    Arguments:
        BaseHTTPMiddleware {_type_} -- the base middleware class to inherit from
    '''

    def __init__(self, app: ASGIApp, options: SecurityHeaderOptions) -> None:
        super().__init__(app)
        self.headers = options.model_dump(exclude_none=True, by_alias=True)

        if options.custom_headers:
            self.headers.update(options.custom_headers)

    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        '''Adds the configured headers to the response

        Arguments:
            request {Request} -- the original request
            call_next {CallNext} -- the next middleware in the chain 

        Returns:
            Response -- the response from the API
        '''
        response = await call_next(request)
        response.headers.update(self.headers)
        return response
