
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.extensions.middleware.request_logger import RequestLoggingMiddleware
from app.extensions.middleware import exc_handlers

from app import build, routing


app = build.create_instance()
build.handle_documentation(app)

build.register_cors(app)
app.add_middleware(RequestLoggingMiddleware)  # type: ignore


@app.exception_handler(RequestValidationError)
async def handle_validation_exc(_: Request, exc: RequestValidationError) -> JSONResponse:
    response_data = await exc_handlers.handle_validation_exc(exc)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data.model_dump(),
        headers={"X-Error-Label": "INVALID_DATA"}
    )


@app.exception_handler(HTTPException)
async def handle_http_exc(request: Request, exc: HTTPException) -> JSONResponse:
    """Handles HTTP exceptions and returns a standardized response."""
    response_data = await exc_handlers.process_http_error(request, exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data.model_dump(),
        headers=exc.headers
    )

routing.register_routers(app)
