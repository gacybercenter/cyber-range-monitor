


from typing import Annotated

from fastapi import APIRouter, Body, status

from range_monitor.auth.depends import AccessTokenDep, TokenServiceDep, UserServiceDep
from range_monitor.auth.schema import (
    LoginRequest,
    TokenDetails,
    TokenRefreshResponse,
    TokenRequestBody,
    TokenResponse,
)
from range_monitor.utils.openapi_extra import api_error

tokens_router = APIRouter()



@tokens_router.post(
    '/tokens/',
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Invalid username or password'),
    },
)
async def create_tokens(
    body: Annotated[LoginRequest, Body(...)],
    user_service: UserServiceDep,
    token_service: TokenServiceDep,
) -> TokenResponse:
    '''
    Authenticates a user and issues a JWT token pair upon successful login.
    The access token is to be used for authenticating API requests, while the refresh
    token can be used to obtain new access tokens when the current one expires.
    '''
    authorized_user = await user_service.authenticate(
        username=body.username,
        password=body.password
    )
    await token_service.cache_cver(
        authorized_user.id,
        authorized_user.cver
    )
    claim = await token_service.create_claims(
        user_id=authorized_user.id,
        role=authorized_user.role,
        cver=authorized_user.cver,
        username=authorized_user.username,
    )

    return TokenResponse(
        claim=claim,
        user_id=authorized_user.id,
        username=authorized_user.username,
        role=authorized_user.role,
    )

@tokens_router.post(
    '/tokens/refresh/',
    response_model=TokenRefreshResponse
)
async def refresh_tokens(
    tokens: Annotated[TokenRequestBody, Body(...)],
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
) -> TokenRefreshResponse:
    '''
    Refreshes an access token using a valid refresh token.
    '''
    refresh_claim = await token_service.verify_token(
        token=tokens.refresh_token,
        token_type='refresh'
    )
    target_user = await user_service.read_user(refresh_claim.sub)

    new_claim = await token_service.refresh_claim(
        old_refresh=refresh_claim,
        access_token=tokens.access_token,
        username=target_user.username,
    )

    return TokenRefreshResponse(
        username=target_user.username,
        id=target_user.id,
        claim=new_claim,
    )


@tokens_router.delete(
    '/tokens/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('Invalid or expired session'),
    },
)
async def delete_tokens(
    tokens: Annotated[TokenRequestBody, Body(...)],
    token_service: TokenServiceDep,
) -> None:
    '''
    Revokes the given refresh token and its associated access token.
    This effectively logs the user out by invalidating their current
    session tokens.
    '''
    await token_service.revoke_tokens(
        refresh_token=tokens.refresh_token,
        access_token=tokens.access_token
    )


@tokens_router.get('/tokens/', response_model=TokenDetails)
async def inspect_access_token(
    token_claim: AccessTokenDep,
    token_service: TokenServiceDep,
) -> TokenDetails:
    '''
    Retrieves details about the currently authenticated access token.
    '''
    return await token_service.inspect(token_claim)