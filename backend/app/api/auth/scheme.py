from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param


class HTTPSessionIdMissing(HTTPException):
    def __init__(self, message: str, header: dict | None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message or 'Session ID is missing.',
            headers=header or {'WWW-Authenticate': 'Bearer'},
        )


class HTTPSessionIDBearer(HTTPBearer):
    def __init__(self) -> None:
        super().__init__(
            scheme_name=self.__class__.__name__,
            description=(
                'Expects client to send a signed session ID in the `Authorization` header'
                ' with the Bearer scheme. Then loads the signature and returns the '
                'unsigned session ID or None if the signature is invalid or expired.'
            ),
            auto_error=True,
        )

    async def __call__(self, request: Request) -> str:
        authorization = request.headers.get('Authorization')
        if not authorization:
            raise HTTPSessionIdMissing(
                message='Authorization header is missing.',
                header={'WWW-Authenticate': 'Bearer'},
            )
        scheme, unsigned_sid = get_authorization_scheme_param(authorization)
        if not unsigned_sid or scheme.lower() != 'bearer':
            raise HTTPSessionIdMissing(
                message='Invalid authorization scheme or session ID is missing.',
                header={'WWW-Authenticate': 'Bearer'},
            )

        return unsigned_sid