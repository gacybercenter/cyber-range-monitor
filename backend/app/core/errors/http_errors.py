from enum import StrEnum
from typing import Optional
from fastapi import HTTPException, status

from .details import HTTPExcDetails

# Custom HTTP Exceptions & Shorthands


class HTTPErrorLabel(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    INVALID_PERMISSIONS = "INVALID_PERMISSIONS"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    BAD_REQUEST = "BAD_REQUEST"
    INVALID_DATA = "INVALID_DATA"


class ApiHTTPException(HTTPException):
    '''base class for api errors to allow for the { details: "" } section to be a custom response 
    for the frontend type safety 
    '''
    def __init__(self, status_code: int, details: HTTPExcDetails, headers: dict = {}) -> None:
        if details.error_label:
            headers["X-Error-Label"] = details.error_label
        self.data = details
        super().__init__(
            status_code=status_code,
            detail=details.message,
            headers=headers
        )


class HTTPNotFound(ApiHTTPException):
    """Raises a 404 Not Found HTTPException - HTTPErrorLabel.NOT_FOUND"""

    def __init__(self, resource_name: str) -> None:
        message = f"{resource_name} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            details=HTTPExcDetails(
                message=message,
                error_label=HTTPErrorLabel.NOT_FOUND
            )
        )


class HTTPUnauthorized(ApiHTTPException):
    """Raises a 401 Unauthorized HTTPException - HTTPErrorLabel.INVALID_PERMISSIONS"""

    def __init__(self, msg: str | None = None, headers: dict = {}) -> None:
        if not msg:
            msg = "You are not authorized to access this resource"
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=HTTPExcDetails(
                message=msg,
                error_label=HTTPErrorLabel.LOGIN_REQUIRED
            ),
            headers=headers
        )


class HTTPForbidden(ApiHTTPException):
    """Raises a 403 Forbidden HTTPException"""

    def __init__(self, msg: str | None, headers: Optional[dict] = None) -> None:
        msg_default = "You have not been granted access to this resource"
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            details=HTTPExcDetails(
                message=msg if msg else msg_default,
                error_label=HTTPErrorLabel.INVALID_PERMISSIONS
            ),
            headers=headers or {}
        )


class HTTPBadRequest(ApiHTTPException):
    """When the client sends a bad request, raises a 400 HTTPException - HTTPErrorLabel.BAD_REQUEST"""

    def __init__(self, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            details=HTTPExcDetails(
                message=msg,
                error_label=HTTPErrorLabel.BAD_REQUEST
            )
        )


class HTTPBadRequestData(ApiHTTPException):
    """When a validation error occurs in a pydantic model, raises a 400 HTTPException - HTTPErrorLabel.INVALID_DATA"""

    def __init__(self, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            details=HTTPExcDetails(
                message=msg,
                error_label=HTTPErrorLabel.INVALID_DATA
            )
        )
