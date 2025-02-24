from fastapi import HTTPException, status

class HTTPInvalidSession(HTTPException):
    '''Raises a 401 Unauthorized HTTPException'''

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid session or expired session'
        )

class HTTPInvalidCredentials(HTTPException):
    '''Raises a 401 Unauthorized HTTPException'''

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )