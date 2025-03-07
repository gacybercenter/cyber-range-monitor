from enum import StrEnum
from fastapi import HTTPException, status

# Custom HTTP Exceptions & Shorthands

class HTTPErrorLabel(StrEnum):
    NOT_FOUND = "NOT_FOUND"
    INVALID_PERMISSIONS = "INVALID_PERMISSIONS"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    BAD_REQUEST = "BAD_REQUEST"
    INVALID_DATA = "INVALID_DATA"

class BaseHTTPException(HTTPException):
    '''base class for api http exceptions that allow for the use of "labels" to 
    assign for the frontend api client to handle the errors that share the same 
    status code.
    '''
    def __init__(self, status_code: int, detail: str, label: str) -> None:
        super().__init__(status_code=status_code, detail=detail)
        self.label = label


class HTTPNotFound(BaseHTTPException):
    """Raises a 404 Not Found HTTPException - HTTPErrorLabel.NOT_FOUND"""

    def __init__(self, resource_name: str, custom_msg: str | None = None) -> None:
        message = f"{resource_name} not found" if not custom_msg else custom_msg
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
            label=HTTPErrorLabel.NOT_FOUND
        )


class HTTPUnauthorized(BaseHTTPException):
    """Raises a 401 Unauthorized HTTPException - HTTPErrorLabel.INVALID_PERMISSIONS"""

    def __init__(self, msg: str | None = None) -> None:
        if not msg:
            msg = "You are not authorized to access this resource"
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg, 
            label=HTTPErrorLabel.LOGIN_REQUIRED
        )

class HTTPInvalidAPIKey(BaseHTTPException):
    """Raises a 401 Unauthorized HTTPException - HTTPErrorLabel.INVALID_PERMISSIONS"""

    def __init__(self, msg: str | None = None) -> None:
        if not msg:
            msg = "Your session is invalid or has expired."
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=msg, 
            label=HTTPErrorLabel.LOGIN_REQUIRED
        )


class HTTPForbidden(BaseHTTPException):
    """Raises a 403 Forbidden HTTPException"""

    def __init__(self, msg: str | None) -> None:
        msg_default = "You have not been granted access to this resource"
        details = msg if msg else msg_default
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=details,
            label=HTTPErrorLabel.INVALID_PERMISSIONS
        )


class HTTPBadRequest(BaseHTTPException):
    """When the client sends a bad request, raises a 400 HTTPException - HTTPErrorLabel.BAD_REQUEST"""

    def __init__(self, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
            label="BAD_REQUEST"
        )

class HTTPInvalidRequestData(BaseHTTPException):
    """When a validation error occurs in a pydantic model, raises a 400 HTTPException - HTTPErrorLabel.INVALID_DATA"""

    def __init__(self, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg,
            label=HTTPErrorLabel.INVALID_DATA
        )