



from fastapi import status

from range_monitor.core.errors import APIException


class InvalidCredentialsError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Invalid Credentials'
    code = 'invalid_credentials'

    def __init__(self) -> None:
        super().__init__(detail='Invalid username or password')


class InvalidJwtToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Invalid Token'

    def __init__(
        self,
        detail: str,
        token_type: str = 'access'
    ) -> None:
        self.code = f'invalid_{token_type}_token'
        super().__init__(
            detail=detail,
            headers={
                'WWW-Authenticate': 'Bearer error="invalid_token"'
            }
        )

class RoleForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    title = 'Forbidden'
    code = 'forbidden'

    def __init__(self) -> None:
        super().__init__(detail='You do not have permission to access this resource')


class TokenRotationError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    title = 'Token Rotation Failed'
    code = 'token_rotation_failed'

    def __init__(self, detail: str) -> None:
        super().__init__(
            detail=detail,
            headers={
                'WWW-Authenticate': f'Bearer error="{self.detail}"'
            }
        )