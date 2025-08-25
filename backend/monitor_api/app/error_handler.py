import traceback
from dataclasses import asdict
from http import HTTPStatus

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from monitor_api.core import constant
from monitor_api.core.exceptions import APIException
from monitor_api.core.pydantic_utils import normalize_pydantic_exception
from monitor_api.infra import APILogger

from .error_schema import ErrorResponse
from .response_class import MsgSpecJSONResponse


def log_exception(
    request: Request, exc: Exception, status: int, msg: str, **extra
) -> None:
    """
    Logs an exception with structured logging.

    Parameters
    ----------
    request : Request
    exc : Exception
    status : int
    msg : str
    """
    APILogger.get_loguru_logger().error(
        msg,
        status_code=status,
        method=request.method,
        url=str(request.url),
        exception_type=exc.__class__.__name__,
        status_phrase=HTTPStatus(status).phrase,
        detail=str(exc),
        **extra,
    )


def handle_api_exception(
    request: Request,
    exc: APIException,
) -> MsgSpecJSONResponse:
    """
    Handles custom API exceptions raised by services or route handlers.

    Parameters
    ----------
    request : Request
    exc : APIException
    Returns
    -------
    MsgSpecJSONResponse
    """
    body = ErrorResponse(
        title=exc.title,
        status=exc.status_code,
        detail=exc.detail,
        instance=request.headers.get(constant.REQUEST_ID_HEADER_NAME, 'N/A'),
        code=exc.code,
        extras=exc.extras if exc.extras else None,
    )

    log_exception(
        request,
        exc,
        exc.status_code,
        f'API Exception occurred: {exc.title}',
        **(exc.extras or {}),
    )

    return MsgSpecJSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(exclude_none=True),
        headers=exc.headers,
        media_type='application/problem+json',
    )


def validation_error_handle(
    request: Request,
    exc: RequestValidationError,
) -> MsgSpecJSONResponse:
    """
    Handles request validation errors from FastAPI/Pydantic

    Parameters
    ----------
    request : Request
    exc : RequestValidationError

    Returns
    -------
    MsgSpecJSONResponse
    """

    normalized_errs = [asdict(err) for err in normalize_pydantic_exception(exc)]

    body = ErrorResponse(
        title='Invalid request',
        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail='The request could not be validated. See extras for details.',
        instance=request.headers.get(constant.REQUEST_ID_HEADER_NAME, 'N/A'),
        code='invalid_request',
        extras={'reason': normalized_errs},
    )

    log_exception(
        request,
        exc,
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        'Request validation error, client provided bad data',
        raw_pydantic=exc.errors(),
        normalized_errors=normalized_errs,
    )

    return MsgSpecJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=body.model_dump(exclude_none=True),
        media_type='application/problem+json',
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> MsgSpecJSONResponse:
    """handles HTTP exceptions from starlette/fasapi"""

    body = ErrorResponse(
        title=HTTPStatus(exc.status_code).phrase,
        status=exc.status_code,
        detail=exc.detail if exc.detail else None,
        instance=request.headers.get(constant.REQUEST_ID_HEADER_NAME, 'N/A'),
        code=None,
        extras=None,
    )

    log_exception(
        request,
        exc,
        exc.status_code,
        f'HTTP Exception occurred: {body.title}',
        **(exc.headers or {}),
    )

    return MsgSpecJSONResponse(
        status_code=exc.status_code,
        content=body.model_dump(exclude_none=True),
        headers=exc.headers,
        media_type='application/problem+json',
    )


def mount_exception_handlers(app: FastAPI) -> None:
    '''
    Registers exception handlers to the FastAPI app.

    Parameters
    ----------
    app : FastAPI
        _description_

    Returns
    -------
    _type_
        _description_
    '''
    @app.exception_handler(APIException)
    async def api_exception_handler(
        request: Request, exc: APIException
    ) -> MsgSpecJSONResponse:
        return handle_api_exception(request, exc)

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> MsgSpecJSONResponse:
        return validation_error_handle(request, exc)

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> MsgSpecJSONResponse:
        return await http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> MsgSpecJSONResponse:
        body = ErrorResponse(
            title='Internal Server Error',
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An internal server error occurred.',
            instance=request.headers.get(constant.REQUEST_ID_HEADER_NAME, 'N/A'),
            code='internal_server_error',
            extras=None,
        )

        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)

        log_exception(
            request,
            exc,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'Unhandled exception occurred, likely a bug in the server.',
            traceback=''.join(tb),
        )

        return MsgSpecJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=body.model_dump(exclude_none=True),
            media_type='application/problem+json',
        )
