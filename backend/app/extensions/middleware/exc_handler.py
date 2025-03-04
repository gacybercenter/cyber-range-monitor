import json
import traceback

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.db.main import get_session
from app.extensions import api_console
from app.schemas.errors import (
    APIErrorResponse,
    APIInternalServerError,
    HTTPErrorDetails,
    normalize_validation_error,
)


def get_error_data(request: Request, exc: HTTPException) -> HTTPErrorDetails:
    """resolves the HTTP exception into a request that can be logged by the server

    Arguments:
        request {Request} -- the request causing the exception
        exc {HTTPException} -- the exception itself
    Returns:
        HTTPErrorDetails -- the details of the error
    """
    err_data = HTTPErrorDetails.from_request(request, exc.status_code, exc.detail)
    if exc.status_code < 500:
        return err_data

    fmt_traceback = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )
    return APIInternalServerError(**err_data.model_dump(), stack_trace=fmt_traceback)


async def process_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    error_data = get_error_data(request, exc)
    async with get_session() as session:
        if exc.status_code >= 500:
            await api_console.critical(json.dumps(error_data.model_dump()), session)
        else:
            await api_console.error(error_data.__repr__(), session, "HTTPException")

    data = error_data.model_dump()
    if exc.status_code >= 500:
        label = "SERVER_ERROR"
        del data["stack_trace"]
    else:
        label = "CLIENT_ERROR"

    response = APIErrorResponse(message=exc.detail, error_label=label, errors=[data])

    return JSONResponse(status_code=exc.status_code, content=response.model_dump())


def register_exc_handlers(app: FastAPI) -> None:
    """Stanardizes the response from the API when an exception is raised
    and implements logging for common client side exceptions.


    Arguments:
        app {FastAPI} -- the app to register the exception handlers to

    Returns:
        void"""

    @app.exception_handler(RequestValidationError)
    async def validation_exc_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        async with get_session() as session:
            await api_console.warning(f"A validation error occured... ({exc})", session)
            err_data = normalize_validation_error(exc)
            await api_console.error(
                f"ERROR_META: {err_data}", session, "ValidationError"
            )
            await session.commit()
            await session.close()

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIErrorResponse(
                message="Validation Error",
                error_label="VALIDATION_ERROR",
                errors=err_data,
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        """
        returns a standardized JSON response for all HTTP exceptions and gives a
        verbose log of the request that caused the exception for Internal Server Errors
        Returns:
            JSONResponse -- a json response with the status code and error message
        """
        return await process_http_error(request, exc)
