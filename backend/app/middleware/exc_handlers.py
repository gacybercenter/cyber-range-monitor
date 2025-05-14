
from http import HTTPStatus
import logging
import traceback

from starlette.requests import Request

from fastapi import FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError

from app.common.errors import (
    HTTPErrorDetails,
    HTTPErrorResponse,
    HTTPValidationError
)


from app.utils.msg_spec_json import MsgSpecJSONResponse


error_logger = logging.getLogger('error')


async def log_http_error(request: Request, exc: HTTPException) -> None:
    """resolves the HTTP exception into a request that can be logged by the server
    and extracts detailed information for internal server errors

    Arguments:
        request {Request} -- the request causing the exception
        exc {HTTPException} -- the exception itself
    Returns:
        HTTPErrorDetails -- the details of the error
    """
    err_data = HTTPErrorDetails.from_request(
        request=request,
        status=exc.status_code,
        exc_details=exc.detail
    )

    if exc.status_code < 500:
        error_logger.warning(str(err_data), exc_info=exc)
        return

    traceback_str = "".join(
        traceback.format_exception(
            type(exc), exc, exc.__traceback__
        )
    )
    log_msg = f'{err_data}\n\nException Traceback:\n\t{traceback_str}'

    error_logger.error(log_msg)


async def http_exception_handler(request: Request, exc: HTTPException) -> MsgSpecJSONResponse:
    '''The exception handler for all HTTP Exceptions raised by the API that normalizes the
    http error so that they are all returned in the same format to the frontend

    Arguments:
        request {Request} -- the request that caused the error
        exc {HTTPException} -- the exception that was raised

    Returns:
        HTTPErrorResponse | HTTPExcDetails -- the normalized error response
    '''
    await log_http_error(request, exc)

    json = HTTPErrorResponse(
        message=exc.detail,
        status_text=HTTPStatus(exc.status_code).phrase,
    ).model_dump()
    return MsgSpecJSONResponse(
        status_code=exc.status_code,
        content=json,
        headers=exc.headers
    )

# even though request isn't used, must match the signature of the handler


async def request_validation_error_handler(
    request: Request,
    exc: RequestValidationError
) -> MsgSpecJSONResponse:
    '''handles exceptions raised by FastAPI's RequestValidationError
    and provides the frontend with an easy to process response detailing 
    the errors that occured

    Arguments:
        exc {RequestValidationError} -- the exception raised by FastAPI

    Returns:
        MsgSpecJSONResponse -- the normalized response
    '''
    error_logger.warning(
        'A client sent invalid data and a Validation Error occured.',
        exc_info=exc
    )

    json = HTTPValidationError.from_exc(exc)
    return MsgSpecJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=json.model_dump()
    )


def register_exc_handlers(app: FastAPI) -> None:
    '''registers the exception handlers for the API

    Arguments:
        app {FastAPI} -- the FastAPI app to register the handlers with
    '''

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler_wrapper(
        request: Request,
        exc: RequestValidationError
    ) -> MsgSpecJSONResponse:
        return await request_validation_error_handler(request, exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler_wrapper(
        request: Request,
        exc: HTTPException
    ) -> MsgSpecJSONResponse:
        return await http_exception_handler(request, exc)
