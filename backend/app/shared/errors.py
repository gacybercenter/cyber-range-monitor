
from email.policy import HTTP
from fastapi import HTTPException, status

# Custom HTTP Exceptions & Shorthands



class HTTPNotFound(HTTPException):
    """Raises a 404 Not Found HTTPException"""

    def __init__(self, resource_name: str, custom_msg: str | None = None) -> None:
        message = f"{resource_name} not found" if not custom_msg else custom_msg
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class HTTPUnauthorized(HTTPException):
    """Raises a 401 Unauthorized HTTPException"""

    def __init__(self, msg: str | None = None) -> None:
        if not msg:
            msg = "Authorization is required to access this resource this attempt has been logged by the server"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)


class HTTPForbidden(HTTPException):
    """Raises a 403 Forbidden HTTPException"""

    def __init__(self, msg: str | None) -> None:
        details = (
            msg
            if msg
            else "You do not have the required permissions to access or modify this resource"
        )
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=details)


class HTTPBadRequest(HTTPException):
    """When the client sends a bad request, raises a 400 HTTPException"""

    def __init__(self, msg: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)


class HTTPInvalidSession(HTTPException):
    """Raises a 401 Unauthorized HTTPException"""

    def __init__(self, msg: str | None = None) -> None:
        if not msg:
            msg = "Invalid session or expired session"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
