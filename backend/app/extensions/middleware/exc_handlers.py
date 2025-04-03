import traceback

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError

from app.core.errors.log_schemas import (
    HTTPErrorDetails,
    InternalServerErrorData
)
from app.core.errors.details import (
    APIErrorResponse,
    HTTPExcDetails,
    HTTPValidationErrorDetails,
    normalize_validation_error,
)

from app.core.errors import ApiHTTPException
import logging
# Module used to register the custom exception handlers for FastAPI
# and to normalize the error responses for the frontend.


error_logger = logging.getLogger("errors")


def get_error_data(request: Request, exc: HTTPException) -> HTTPErrorDetails:
    """resolves the HTTP exception into a request that can be logged by the server

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
        return err_data

    fmt_traceback = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    return InternalServerErrorData(**err_data.model_dump(), stack_trace=fmt_traceback)


async def process_http_error(request: Request, exc: HTTPException) -> APIErrorResponse | HTTPExcDetails:
    '''normalizes the http error so that they are all returned in the same format

    Arguments:
        request {Request} -- the request that caused the error
        exc {HTTPException} -- the exception that was raised

    Returns:
        APIErrorResponse | HTTPExcDetails -- the normalized error response
    '''
    error_data = get_error_data(request, exc)
    if exc.status_code >= 500:
        error_logger.critical(
            '[bold red] Unhandled exception raised [/bold red]', exc_info=exc)
    else:
        error_logger.warning(
            f'[yellow] HTTP Exception raised [/yellow] - {exc.status_code} {exc.detail}'
        )

    if isinstance(exc, ApiHTTPException):
        return exc.data

    data = error_data.model_dump()
    if exc.status_code >= 500:
        label = "SERVER_ERROR"
        del data["stack_trace"]
    else:
        label = "CLIENT_ERROR"
    del data["headers"]

    return APIErrorResponse(
        message=exc.detail,
        error_label=label,
    )


async def handle_validation_exc(exc: RequestValidationError) -> HTTPValidationErrorDetails:
    '''handles exceptions raised by FastAPI's RequestValidationError
    and provides the frontend with an easy to process response detailing 
    the errors that occured

    Arguments:
        exc {RequestValidationError} -- the exception raised by FastAPI

    Returns:
        JSONResponse -- the normalized response
    '''
    error_logger.warning(
        f"[italic yellow] A validation error occured [/italic yellow]", exc_info=exc)
    err_data = normalize_validation_error(exc)

    return HTTPValidationErrorDetails(
        errors=err_data,
        error_label="VALIDATION_ERROR"
    )
