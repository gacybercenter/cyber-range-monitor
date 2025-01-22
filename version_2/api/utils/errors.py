from fastapi import HTTPException, status
from typing import Optional

# Custom API Exceptions & Shorthands

class ResourceNotFound(HTTPException):
    def __init__(self, resource_name: str, custom_msg: Optional[str] = None) -> None:
        message = f'{resource_name} not found' if not custom_msg else custom_msg
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class AuthorizationRequired(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization is required to access this resource this attempt has been logged by the server'
        )


class ForbiddenAction(HTTPException):
    def __init__(self, msg: Optional[str]) -> None:
        details = msg if msg else 'You do not have the required permissions to access or modify this resource'
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=details
        )


class BadRequest(HTTPException):
    '''When the client sends a bad request'''
    def __init__(self, msg: str) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg
        )

class HTTPUnauthorizedToken(HTTPException):
    '''Raised when a token is invalid or expired'''

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired login token, please try again',
            headers={'WWW-Authenticate': 'Bearer'}
        )

