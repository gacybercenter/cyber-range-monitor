from fastapi import status

from range_monitor.core.errors import APIError


class InvalidCredentialsError(APIError):
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Invalid Credentials'
    code = 'invalid_credentials'

    def __init__(self) -> None:
        super().__init__(detail='Invalid username or password')
