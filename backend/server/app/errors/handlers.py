from typing import cast

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarleteHTTPException
from starlette.requests import Request

from server.app.errors.hooks_abc import APIErrorHandler, ErrorHook
from server.app.errors.http import HttpError
from server.app.schema import ErrorResponse
from server.schema import normalize_validation_error


class HttpErrorHandler(ErrorHook[HttpError]):
    handles = HttpError

    def get_logger_details(
        self, request: Request, exception: HttpError
    ) -> tuple[str, dict]:
        message = (
            f'[{exception.status_code}, {exception.code}] An HTTP Error failed during a '
            f'{request.method} request to {request.url} from client {request.client} '
            f'detail: {exception.detail}'
        )
        details = {
            'status_code': exception.status_code,
            'error_code': exception.code,
            'headers': exception.headers,
            'correlation_id': request.headers.get('X-Request-ID', 'N/A'),
            'method': request.method,
            'detail': exception.detail,
            'url': str(request.url),
            'service_name': getattr(exception, 'service_name', 'N/A'),
            'reason': getattr(exception, 'reason', 'N/A'),
        }
        return message, details

    def get_response_model(self, exception: HttpError) -> ErrorResponse:
        return ErrorResponse(
            status=exception.status_code,
            code=exception.code,
            detail=exception.detail,
        )


class ValidationErrorHandler(ErrorHook[RequestValidationError]):
    handles = RequestValidationError

    def get_logger_details(
        self,
        request: Request,
        exception: RequestValidationError,
    ) -> tuple[str, dict]:
        message = (
            f'A Pydantic Validation Error of type {type(exception)} occurred during a '
            f'{request.method} request to {request.url} from client {request.client}.'
        )
        details = {
            'correlation_id': request.headers.get('X-Request-ID', 'N/A'),
            'method': request.method,
            'url': str(request.url),
            'errors': exception.errors(),
        }
        return message, details

    def get_response_model(
        self,
        exception: RequestValidationError,
    ) -> ErrorResponse:
        norm_errors = normalize_validation_error(exception)

        return ErrorResponse(
            status=400,
            code='validation_error',
            detail='There was an error validating the request data.',
            extras=cast('dict', norm_errors),
        )


class StarletteErrorHandler(ErrorHook[StarleteHTTPException]):
    '''
    catches both lower level starlette HTTP exceptions
    and fastapi HTTP exceptions as they both inherit from `StarletteHTTPException`
    '''

    handles = StarleteHTTPException

    def get_logger_details(
        self, request: Request, exception: StarleteHTTPException
    ) -> tuple[str, dict]:
        message = (
            f'[{exception.status_code}] A Starlette HTTP Exception of type '
            f'{type(exception)} {request.method} request to {request.url} from client '
            f'{request.client} detail: {exception.detail}'
        )
        details = {
            'status_code': exception.status_code,
            'correlation_id': request.headers.get('X-Request-ID', 'N/A'),
            'method': request.method,
            'detail': exception.detail,
            'url': str(request.url),
        }
        return message, details

    def get_response_model(self, exception: StarleteHTTPException) -> ErrorResponse:
        return ErrorResponse(
            status=exception.status_code,
            code='framework_error',
            detail=exception.detail,
        )


class GenericExceptionHandler(ErrorHook[Exception]):
    handles = Exception

    def get_logger_details(
        self, request: Request, exception: Exception
    ) -> tuple[str, dict]:
        message = (
            f'An unhandled exception of type {type(exception)} occurred during a '
            f'{request.method} request to {request.url} from client {request.client}. '
            f'Exception message: {exception!s}'
        )
        details = {
            'correlation_id': request.headers.get('X-Request-ID', 'N/A'),
            'method': request.method,
            'url': str(request.url),
            'exception_type': str(type(exception)),
            'exception_message': str(exception),
            'traceback': repr(exception.__traceback__),
        }
        return message, details

    def get_response_model(self, exception: Exception) -> ErrorResponse:
        return ErrorResponse(
            status=500,
            code='internal_server_error',
            detail='An internal server error occurred.',
        )


def register_exception_handlers(app: FastAPI) -> None:
    '''
    Register all exception handlers with the FastAPI application

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance
    '''
    hooks: list[type[ErrorHook]] = [
        HttpErrorHandler,
        ValidationErrorHandler,
        StarletteErrorHandler,
        GenericExceptionHandler,
    ]
    for hook_cls in hooks:
        hook = hook_cls()
        app.add_exception_handler(hook.handles, handler=APIErrorHandler(hook))
