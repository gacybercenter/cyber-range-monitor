from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import enum
from typing import Optional, Any
from httpx import head
from pydantic import BaseModel, ValidationError


class ErrorType(str, enum.Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    SYSTEM_ERROR = "SYSTEM_ERROR"


class ResourceNotFound(HTTPException):
    def __init__(self, resource_name: str, custom_msg: Optional[str] = None) -> None:
        message = f'{
            resource_name} not found' if not custom_msg else custom_msg
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class AuthorizationRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization is required to access this resource this attempt has been logged by the server'
        )


class AuthenticationRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Authentication is required to access this resource, please login.'
        )


class HTTPUnauthorizedToken(HTTPException):
    '''Raised when a token is invalid or expired'''

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired login token, please try again',
            headers={'WWW-Authenticate': 'Bearer'}
        )


class APIError(BaseModel):
    error_type: ErrorType
    message: str
    details: dict[str, Any] = {}


class ValidationErrorInfo(BaseModel):
    message: str
    error_details: dict[str, dict]


def handle_validation_error(exc: ValidationError):
    error_details = {}
    for error in exc.errors():
        field_path = " -> ".join(str(x) for x in error["loc"])
        error_details[field_path] = {
            'message': error.get('msg', ''),
            'input': error.get('input', '')
        }
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=APIError(
            error_type=ErrorType.VALIDATION_ERROR,
            message='Validation error',
            details=error_details
        ).model_dump()
    )


def handle_http_error(request, exc: HTTPException) -> JSONResponse:
    # TODO: add logging and severity levels using the enum and some sort of
    # way to obfuscate and handle internal server errors
    error_type = ErrorType.SYSTEM_ERROR
    match exc.status_code:
        case status.HTTP_404_NOT_FOUND:
            error_type = ErrorType.NOT_FOUND

        case status.HTTP_401_UNAUTHORIZED:
            error_type = ErrorType.AUTHENTICATION_ERROR

        case status.HTTP_403_FORBIDDEN:
            error_type = ErrorType.AUTHORIZATION_ERROR

    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            error_type=error_type,
            message=exc.detail
        ).model_dump()
    )


def register_error_handler(app: FastAPI):
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=handle_validation_error(exc)
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException) -> JSONResponse:
        return handle_http_error(request, exc)
