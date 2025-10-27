import abc
import logging
from typing import TypeVar, cast

from fastapi import BackgroundTasks
from starlette.requests import Request
from starlette.responses import Response

from server.app.schema import ErrorResponse
from server.logger import get_loguru_logger
from server.response import MsgspecJsonResponse

E = TypeVar('E', bound=Exception)


def get_status_severity(status_code: int) -> int:
    if 500 <= status_code < 600:
        return logging.ERROR

    if 401 <= status_code < 403:
        return logging.INFO + 5  # SECURITY

    return logging.WARNING


async def log_http_exception(  # noqa: RUF029
    message: str,
    error_info: dict,
    status_code: int,
) -> None:
    log_severity = get_status_severity(status_code)
    logger = get_loguru_logger('server.app.handler', **error_info)
    logger.log(log_severity, message)


class ErrorHook[E: Exception](abc.ABC):
    '''
    An abstract base class for defining

    - What log message and structured log details to
    produce via `get_logger_details`

    - What should the response model be via `get_response_model`
    '''

    handles: type[E] | int

    @abc.abstractmethod
    def get_logger_details(self, request: Request, exception: E) -> tuple[str, dict]: ...

    @abc.abstractmethod
    def get_response_model(self, exception: E) -> ErrorResponse: ...


class APIErrorHandler[E: Exception]:
    '''
    Automatically implements structured logging
    and failing quick and safely by using the given ErrorHook
    implementation.

    All logs are delegated to a background task to return ASAP,
    exceptions are already slow as is.
    '''

    def __init__(self, hook: ErrorHook[E]) -> None:
        self.hook = hook

    async def __call__(self, request: Request, exc: Exception) -> Response:
        exception = cast('E', exc)
        message, error_info = self.hook.get_logger_details(request, exception)
        response = self.hook.get_response_model(exception)
        # force logging to background task to return response ASAP
        bg_tasks = BackgroundTasks()
        bg_tasks.add_task(
            log_http_exception,
            message,
            error_info,
            response.status,
        )
        return MsgspecJsonResponse(
            status_code=response.status,
            content=response.dump(),
            headers=getattr(exc, 'headers', None),
            background=bg_tasks,
        )
