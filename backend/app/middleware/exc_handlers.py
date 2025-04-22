
import traceback

from starlette.requests import Request

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import (
    HTTPErrorDetails,
    APIErrorResponse,
    HTTPValidationErrorDetails,
    PydanticError
)

from app.misc.logging import APILogging
from app.misc import event_logger

from app.db.core import get_session
from pydantic import ValidationError

from app.core.errors import ApiHTTPException

error_logger = APILogging.middleware()


async def log_http_error(request: Request, exc: HTTPException) -> str:
    """resolves the HTTP exception into a request that can be logged by the server
    and extracts detailed information for internal server errors

    Arguments:
        request {Request} -- the request causing the exception
        exc {HTTPException} -- the exception itself
    Returns:
        HTTPErrorDetails -- the details of the error
    """
    err_data = HTTPErrorDetails.from_request(
        request, exc.status_code, exc.detail
    )
    if exc.status_code < 500:
        error_logger.warning(str(err_data), exc_info=exc)
        return 'CLIENT_ERROR'

    traceback_str = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    log_msg = f'{err_data}\n\nException Traceback:\n\t{traceback_str}'

    error_logger.critical(log_msg)
    async with get_session() as session:
        await event_logger.critical(log_msg, session)

    return 'SERVER_ERROR'


def normalize_validation_error(
    err: ValidationError | RequestValidationError,
) -> list[PydanticError]:
    """normalizes the format of a validation error

    Arguments:
        err {ValidationError} -- the error raised

    Returns:
        list[dict] -- the errors in a normalized format
    """
    error_list = []
    for details in err.errors():
        error_data = PydanticError(
            field=".".join(str(loc) for loc in details.get("loc", [])),
            message=details.get("msg", "Invalid data."),
            type=details.get("type", "Unknown"),
        )
        error_list.append(error_data)

    return error_list


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    '''The exception handler for all HTTP Exceptions raised by the API that normalizes the
    http error so that they are all returned in the same format to the frontend

    Arguments:
        request {Request} -- the request that caused the error
        exc {HTTPException} -- the exception that was raised

    Returns:
        APIErrorResponse | HTTPExcDetails -- the normalized error response
    '''
    error_label = await log_http_error(request, exc)
    if isinstance(exc, ApiHTTPException):
        json = exc.data.model_dump()
    else:
        json = APIErrorResponse(
            message=exc.detail,
            error_label=error_label
        ).model_dump()
    return JSONResponse(
        status_code=exc.status_code,
        content=json,
        headers=exc.headers
    )

async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    '''handles exceptions raised by FastAPI's RequestValidationError
    and provides the frontend with an easy to process response detailing 
    the errors that occured

    Arguments:
        exc {RequestValidationError} -- the exception raised by FastAPI

    Returns:
        JSONResponse -- the normalized response
    '''
    error_logger.warning(
        'A client sent invalid data and a Validation Error occured.', exc_info=exc)
    err_data = normalize_validation_error(exc)

    json = HTTPValidationErrorDetails(
        errors=err_data,
        error_label="VALIDATION_ERROR"
    ).model_dump()

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=json
    )
