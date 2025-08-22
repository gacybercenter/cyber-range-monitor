from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
from fastapi.security.utils import get_authorization_scheme_param

from app.infrastructure.security.signatures import IdSignerService

from .settings import auth_settings


class HTTPSessionIdMissing(HTTPException):
    def __init__(self, message: str, header: dict | None) -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message or 'Session ID is missing.',
            headers=header or {'WWW-Authenticate': 'Bearer'},
        )


class HTTPSessionIDBearer(HTTPBearer):
    def __init__(
        self, header_name: str = 'Authorization', *, id_max_age: int | None = None
    ) -> None:
        super().__init__(
            scheme_name=self.__class__.__name__,
            description=(
                f'Expects client to send a signed session ID in the `{header_name}` header'
                ' with the Bearer scheme. Then loads the signature and returns the '
                'unsigned session ID or None if the signature is invalid or expired.'
            ),
            auto_error=True,
        )
        self.header_name: str = header_name
        self.id_max_age: int = id_max_age or auth_settings.max_age

    async def __call__(self, request: Request) -> str | None:
        authorization = request.headers.get(self.header_name)
        if not authorization:
            raise HTTPSessionIdMissing(
                message='Authorization header is missing.',
                header={'WWW-Authenticate': 'Bearer'},
            )
        signer = IdSignerService()
        scheme, unsigned_sid = get_authorization_scheme_param(authorization)
        if not unsigned_sid or scheme.lower() != 'bearer':
            raise HTTPSessionIdMissing(
                message='Invalid authorization scheme or session ID is missing.',
                header={'WWW-Authenticate': 'Bearer'},
            )

        return signer.load_signed_id(
            unsigned_sid,
            max_age=self.id_max_age
        )

SessionIDBearer = HTTPSessionIDBearer()