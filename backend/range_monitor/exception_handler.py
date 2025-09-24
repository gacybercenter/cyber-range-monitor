import traceback
from http import HTTPStatus

from fastapi import status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from range_monitor import log
from range_monitor.core import constant
from range_monitor.core.errors import APIException
from range_monitor.core.pydantic import SchemaUtils

from .core.api_error_model import ErrorResponse
from .utils.response_class import MsgspecJsonResponse


class ErrorUtils:
    @staticmethod
    def make_response(
        *,
        body: ErrorResponse,
        status_code: int,
        headers: dict[str, str] | None = None,
    ) -> MsgspecJsonResponse:
        return MsgspecJsonResponse(
            status_code=status_code,
            content=body.model_dump(exclude_none=True),
            headers=headers,
            media_type='application/problem+json',
        )

    @staticmethod
    def log_error(
        request: Request, exc: Exception, status: int, msg: str, **extra
    ) -> None:
        """
        Logs an error with structured logging.

        Parameters
        ----------
        request : Request
        exc : Exception
        status : int
        msg : str
        """
        log.get_loguru_logger().error(
            msg,
            status_code=status,
            method=request.method,
            url=str(request.url),
            exception_type=exc.__class__.__name__,
            status_phrase=HTTPStatus(status).phrase,
            detail=str(exc),
            **extra,
        )

    @staticmethod
    def get_instance(request: Request) -> str:
        return request.headers.get(constant.REQUEST_ID_HEADER_NAME, 'N/A')


class ExceptionHandlers:
    @staticmethod
    async def api_exception(request: Request, exc: APIException) -> MsgspecJsonResponse:
        """
        Handles custom API exceptions raised by services or route handlers.

        Parameters
        ----------
        request : Request
        exc : APIException
        Returns
        -------
        MsgspecJsonResponse
        """
        body = ErrorResponse(
            title=exc.title,
            status=exc.status_code,
            detail=exc.detail,
            instance=ErrorUtils.get_instance(request),
            code=exc.code,
            extras=exc.extras if exc.extras else None,
        )
        ErrorUtils.log_error(
            request,
            exc,
            exc.status_code,
            f'API Exception occurred: {body.title}',
            **(exc.headers or {}),
        )
        return ErrorUtils.make_response(
            body=body,
            status_code=exc.status_code,
            headers=exc.headers,
        )

    @staticmethod
    async def request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> MsgspecJsonResponse:
        """
        Handles request validation errors from FastAPI/Pydantic

        Parameters
        ----------
        request : Request
        exc : RequestValidationError

        Returns
        -------
        MsgspecJsonResponse
        """

        normalized_errs = SchemaUtils.get_pydantic_errors(exc)

        body = ErrorResponse(
            title='Invalid request',
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='The request could not be validated. See extras for details.',
            instance=ErrorUtils.get_instance(request),
            code='invalid_request',
            extras={'reason': normalized_errs},
        )

        ErrorUtils.log_error(
            request,
            exc,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            'Request validation error, client provided bad data',
            raw_pydantic=exc.errors(),
            normalized_errors=normalized_errs,
        )

        return ErrorUtils.make_response(
            body=body,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @staticmethod
    async def starlette_http_exception(
        request: Request, exc: HTTPException
    ) -> MsgspecJsonResponse:
        """handles HTTP exceptions from starlette/fasapi"""

        body = ErrorResponse(
            title=HTTPStatus(exc.status_code).phrase,
            status=exc.status_code,
            detail=exc.detail if exc.detail else None,
            instance=ErrorUtils.get_instance(request),
            code=None,
            extras=None,
        )
        ErrorUtils.log_error(
            request,
            exc,
            exc.status_code,
            f'HTTP Exception occurred: {body.title}',
            **(exc.headers or {}),
        )
        return ErrorUtils.make_response(
            body=body,
            status_code=exc.status_code,
            headers=exc.headers,  # type: ignore
        )

    @staticmethod
    async def general_exception(
        request: Request, exc: Exception
    ) -> MsgspecJsonResponse:
        """
        Handles uncaught exceptions.

        Parameters
        ----------
        request : Request
        exc : Exception

        Returns
        -------
        MsgspecJsonResponse
        """
        message = (
            'Oops something went wrong, contact and administrator '
            'if the issue persists.'
        )

        body = ErrorResponse(
            title='Request Failed',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
            instance=ErrorUtils.get_instance(request),
            code='internal_server_error',
            extras=None,
        )

        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)

        ErrorUtils.log_error(
            request,
            exc,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'Unhandled exception occurred, likely a bug in the server.',
            traceback=''.join(tb),
        )

        return ErrorUtils.make_response(
            body=body,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
