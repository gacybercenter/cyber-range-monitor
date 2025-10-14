from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body, Security, status

from range_monitor.auth.depends import AccessTokenDep, AuthServiceDep, oauth2_token
from range_monitor.auth.schema import RefreshRequest
from range_monitor.users.depends import UsersServiceDep
from range_monitor.users.schema import (
    LoginRequest,
    TokenClaim,
    TokenDetails,
    TokenRequestBody,
    TokenResponse,
    TokenUser,
)
from range_monitor.utils.openapi_extra import Error

auth_router = APIRouter()


@auth_router.post(
    '/login/',
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Invalid username or password'),
    },
)
async def login_user(
    body: Annotated[LoginRequest, Body(...)],
    user_service: UsersServiceDep,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    """
    Authenticates a user and issues a JWT token pair upon successful login.
    The access token is to be used for authenticating API requests, while the refresh
    token can be used to obtain new access tokens when the current one expires.
    """
    user = await user_service.check_credentials(
        username=body.username, password=body.password
    )
    tokens = await auth_service.authorize(
        user_id=user.id, cver=user.cver, role=user.role
    )
    await user_service.update_last_login(user_id=user.id)
    return TokenResponse(
        user_id=user.id, username=user.username, role=user.role, claim=tokens
    )


@auth_router.post(
    '/refresh/',
    response_model=TokenClaim,
)
async def refresh_tokens(
    access_token: Annotated[str, Security(oauth2_token)],
    body: Annotated[RefreshRequest, Body(...)],
    auth_service: AuthServiceDep,
) -> TokenClaim:
    """
    **protected**
    Refreshes an access token using a valid refresh token
    returning the rotated token claims. The access token
    in the auth header does not need to be valid.
    """
    return await auth_service.refresh_tokens(body, access_token)


@auth_router.get('/token', response_model=TokenDetails)
async def get_token_user(
    access_token: AccessTokenDep,
    user_service: UsersServiceDep,
) -> TokenDetails:
    """
    **protected**
    Retrieves details about the currently authenticated access token.
    The provided token must be a valid access token.
    """
    owner = await user_service.read_user(access_token.user_id)

    token_user = TokenUser(
        user_id=owner.id,
        username=owner.username,
        role=owner.role,
        cver=owner.credential_version,
    )

    return TokenDetails(
        user=token_user,
        issued_at=datetime.fromtimestamp(access_token.iat),
        expires_at=datetime.fromtimestamp(access_token.exp),
        time_to_live=access_token.time_to_live,
    )


@auth_router.delete(
    '/logout/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('Invalid or expired session'),
    },
)
async def logout_user(
    tokens: Annotated[TokenRequestBody, Body(...)],
    auth_service: AuthServiceDep,
) -> None:
    """
    **protected**
    Revokes the given refresh token and its associated access token.
    This effectively logs the user out by invalidating their current
    session tokens.
    """
    access_claim = auth_service.get_token_claim(
        tokens.access_token, expected_type='access'
    )
    await auth_service.revoke_tokens(
        access_claim=access_claim, refresh_token=tokens.refresh_token
    )
