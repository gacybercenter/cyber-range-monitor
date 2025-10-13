import logging
import traceback
from http import HTTPStatus

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.requests import Request

from range_monitor.core import correlation_id
from range_monitor.core.errors import APIError, DatabaseFailure, HttpTransportViolation
from range_monitor.core.schema import get_pydantic_errors
from range_monitor.schema.errors import ErrorResponse
from range_monitor.utils.response_class import MsgspecJsonResponse

logger = logging.getLogger(__name__)


def create_error_log(
    message: str,
    *,
    request: Request,
    error: BaseException,
    extras: dict | None = None,
) -> None:
    status_code = request.scope.get('status_code', HTTPStatus.INTERNAL_SERVER_ERROR)
    cor_id = correlation_id.get_id()
    base_extra = {
        'method': request.method,
        'url': str(request.url),
        'status_code': status_code,
        'correlation_id': cor_id,
        'exception_type': error.__class__.__name__,
        'detail': str(error),
    }

    logger.error(msg=message, extra={**base_extra, **(extras or {})}, exc_info=error)


def error_response_json(
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


def get_instance(request: Request) -> str:
    return request.headers.get('X-Request-ID', 'N/A')


async def api_exception_handler(request: Request, exc: APIError) -> MsgspecJsonResponse:
    """
    Handles custom API exceptions raised by services or route handlers.

    Parameters
    ----------
    request : Request
    exc : APIError
    Returns
    -------
    MsgspecJsonResponse
    """
    body = ErrorResponse(
        status=exc.status_code,
        detail=exc.detail,
        request_id=get_instance(request),
        code=exc.code,
        extras=exc.extras if exc.extras else None,
    )

    create_error_log(
        f'API Exception occurred: {body.detail}',
        request=request,
        error=exc,
        extras={'detail': body.detail, 'code': body.code, **exc.extras},
    )

    return error_response_json(
        body=body,
        status_code=exc.status_code,
        headers=exc.headers,
    )


async def validation_error_handler(
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
    normalized_errs = get_pydantic_errors(exc)

    body = ErrorResponse(
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail='The request could not be validated. See extras for details.',
        request_id=get_instance(request),
        code='invalid_request',
        extras={'reason': normalized_errs},
    )

    create_error_log(
        'Request validation error occurred.',
        request=request,
        error=exc,
        extras={
            'detail': body.detail,
            'code': body.code,
            'errors': normalized_errs,
        },
    )

    return error_response_json(
        body=body,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


async def starlette_http_exception(
    request: Request, exc: HTTPException
) -> MsgspecJsonResponse:
    """handles HTTP exceptions from starlette/fasapi"""

    body = ErrorResponse(
        status=exc.status_code,
        detail=exc.detail if exc.detail else None,
        request_id=get_instance(request),
        code=None,
        extras=None,
    )
    create_error_log(
        'HTTP exception occurred.',
        request=request,
        error=exc,
        extras={
            'code': body.code,
            'correlation_id': body.request_id,
        },
    )
    return error_response_json(
        body=body,
        status_code=exc.status_code,
        headers=exc.headers,  # type: ignore
    )


async def general_exception_handler(
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
        'Oops something went wrong, contact and administrator if the issue persists.'
    )

    body = ErrorResponse(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=message,
        request_id=get_instance(request),
        code='internal_server_error',
        extras=None,
    )

    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)

    create_error_log(
        f'Unhandled exception occurred, {exc.__class__.__name__}: {str(exc)}',
        request=request,
        error=exc,
        extras={
            'correlation_id': body.request_id,
            'traceback': tb,
            'exception_type': exc.__class__.__name__,
        },
    )

    return error_response_json(
        body=body,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


async def transport_error_handler(
    request: Request, exc: HttpTransportViolation
) -> MsgspecJsonResponse:
    """
    Handles `HttpTransportViolation` exceptions raised when a transport
    encounters an invalid or suspicious URL scheme.

    Parameters
    ----------
    request : Request
    exc : HttpTransportViolation

    Returns
    -------
    MsgspecJsonResponse
    """
    msg = (
        f'The request could not be processed due to the {exc.tenant} transport '
        'having an invalid URL scheme. Please contact an administrator to edit the'
        f' {exc.tenant} transport settings.'
    )

    body = ErrorResponse(
        status=status.HTTP_423_LOCKED,
        detail=msg,
        request_id=get_instance(request),
        code=f'{exc.tenant}_transport_violation',
        extras={'reason': str(exc)},
    )

    create_error_log(
        f'Tenant {exc.tenant} transport violation: {body.detail}',
        request=request,
        error=exc,
        extras={
            'detail': body.detail,
            'code': body.code,
            'correlation_id': body.request_id,
            'reason': str(exc),
        },
    )

    return error_response_json(
        body=body,
        status_code=status.HTTP_423_LOCKED,
    )


async def database_failure_handler(
    request: Request, exc: DatabaseFailure
) -> MsgspecJsonResponse:
    """
    Handles `DatabaseFailure` exceptions raised when a database operation
    fails.

    Parameters
    ----------
    request : Request
    exc : DatabaseFailure

    Returns
    -------
    MsgspecJsonResponse
    """
    msg = (
        'The request could not be processed due to an error on our side. '
        'Please try again later.'
    )

    body = ErrorResponse(
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=msg,
        request_id=get_instance(request),
        code='database_failure',
    )

    create_error_log(
        'Database failure occurred.',
        request=request,
        error=exc,
        extras={
            'detail': body.detail,
            'code': body.code,
            'correlation_id': body.request_id,
            'reason': str(exc),
            'operation': exc.operation,
        },
    )

    return error_response_json(
        body=body,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def add_handlers(app: FastAPI) -> None:
    """
    Adds exception handlers to the FastAPI app.

    Parameters
    ----------
    app : FastAPI
    """
    app.add_exception_handler(APIError, api_exception_handler)  # type: ignore
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,  # type: ignore
    )
    app.add_exception_handler(HTTPException, starlette_http_exception)  # type: ignore
    app.add_exception_handler(HttpTransportViolation, transport_error_handler)  # type: ignore
    app.add_exception_handler(DatabaseFailure, database_failure_handler)  # type: ignore
    app.add_exception_handler(Exception, general_exception_handler)
