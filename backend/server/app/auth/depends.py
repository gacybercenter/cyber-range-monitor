from typing import Annotated

from fastapi import Depends, Security

from server.app.auth.repo import TokenStore
from server.app.auth.schema import AccessToken, RefreshToken
from server.app.auth.schemes import OAuth2Token, RefreshTokenCookie
from server.app.auth.service import AuthenticationService
from server.app.depends import RedisDep


async def get_token_store(redis: RedisDep) -> TokenStore:  # noqa: RUF029
    return TokenStore(redis=redis)


TokenStoreDep = Annotated[TokenStore, Depends(get_token_store)]


async def get_authentication_service(  # noqa: RUF029
    tokens: TokenStoreDep,
) -> AuthenticationService:
    return AuthenticationService(tokens=tokens)


AuthServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]

oauth2_token = OAuth2Token()
refresh_token = RefreshTokenCookie()

AccessTokenRequired = Annotated[str, Security(oauth2_token)]
RefreshTokenRequired = Annotated[str, Security(refresh_token)]


async def check_access_token(
    token: AccessTokenRequired,
    auth_service: AuthServiceDep
) -> AccessToken:
    return await auth_service.verify_access_token(token)


async def check_refresh_token(
    token: RefreshTokenRequired,
    auth_service: AuthServiceDep
) -> RefreshToken:
    return await auth_service.verify_refresh_token(token)


AccessTokenDep = Annotated[AccessToken, Security(check_access_token)]
RefreshTokenDep = Annotated[RefreshToken, Security(check_refresh_token)]
