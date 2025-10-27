from fastapi import Request
from fastapi.security import APIKeyCookie, HTTPBearer

from server.app.auth.errors import TokenMissingError
from server.app.errors.http import UnauthorizedError

_COOKIE_NAME = 'refresh_token'


class RefreshTokenCookie(APIKeyCookie):
    def __init__(
        self,
        *,
        name: str = _COOKIE_NAME,
    ) -> None:
        super().__init__(
            name=name,
            scheme_name='RefreshTokenCookie',
            description=('Cookie containing the refresh token for authentication.'),
            auto_error=False,
        )

    async def __call__(self, request: Request) -> str | None:
        refresh_token = await super().__call__(request)
        if not refresh_token:
            raise UnauthorizedError('refresh_token_missing')
        return refresh_token


class OAuth2Token(HTTPBearer):
    '''
    Requires a Bearer token in the Authorization header
    '''

    def __init__(self) -> None:
        super().__init__(
            description='Bearer authentication with JWT tokens.', auto_error=False
        )

    async def __call__(self, request: Request) -> str:
        auth = await super().__call__(request)
        if not auth or not auth.scheme.lower() == 'bearer':
            raise TokenMissingError

        return auth.credentials
