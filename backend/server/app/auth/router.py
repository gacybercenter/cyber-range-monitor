from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Response, status

from server.app.auth.depends import (
    AccessTokenDep,
    AuthServiceDep,
    RefreshTokenDep,
    RefreshTokenRequired,
)
from server.app.auth.schema import (
    AccessToken,
    SessionList,
    TokenClaim,
)
from server.app.errors.http import ForbiddenError
from server.app.openapi_extra import Error
from server.app.users.depends import AuthorizedAdmin, UsersServiceDep
from server.app.users.schema import (
    LoginUserBody,
    LoginUserResponse,
)
from server.headers import ClientInfoDep

auth_router = APIRouter()


@auth_router.post(
    '/login/',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Invalid username or password'),
    },
)
async def login_user(
    response: Response,
    client_info: ClientInfoDep,
    body: Annotated[LoginUserBody, Body(...)],
    user_service: UsersServiceDep,
    auth_service: AuthServiceDep,
) -> LoginUserResponse:
    """
    Authenticates a user and issues a JWT token pair upon successful login.
    The access token is to be used for authenticating API requests, while the refresh
    token can be used to obtain new access tokens when the current one expires.
    """
    user = await user_service.check_credentials(
        username=body.username, password=body.password
    )

    tokens = await auth_service.authorize(
        user=user, client=client_info, response=response
    )
    await user_service.update_login_date(user.id)
    return LoginUserResponse(
        user_id=user.id, username=user.username, role=user.role, claim=tokens
    )


@auth_router.post('/refresh/')
async def refresh_session(
    refresh_token: RefreshTokenDep,
    response: Response,
    client: ClientInfoDep,
    auth_service: AuthServiceDep,
    user_service: UsersServiceDep,
) -> TokenClaim:
    """
    **protected**
    Refreshes an access token using a valid refresh token
    returning the rotated token claims. The access token
    in the auth header does not need to be valid.
    """
    session_owner = await user_service.get_token_user(refresh_token.sub)
    if not session_owner:
        raise ForbiddenError('Invalid session owner')

    new_claim = await auth_service.refresh_session(
        refresh_token, client, response, session_owner
    )
    return new_claim


@auth_router.get('/token/')
async def get_token_user(access_token: AccessTokenDep) -> AccessToken:
    """
    **protected**
    Retrieves details about the currently authenticated access token.
    The provided token must be a valid access token.
    """
    return access_token


@auth_router.delete(
    '/logout/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('Invalid or expired session'),
    },
)
async def logout_user(
    response: Response,
    access_token: AccessTokenDep,
    refresh_token: RefreshTokenRequired,
    auth_service: AuthServiceDep,
) -> None:
    """
    **protected**
    Revokes the given refresh token and its associated access token.
    This effectively logs the user out by invalidating their current
    session tokens.
    """
    await auth_service.end_session(
        user_id=access_token.sub,
        session_id=access_token.sid,
        response=response,
    )


@auth_router.get('/sessions/')
async def list_sessions(
    access_token: AccessTokenDep,
    auth_service: AuthServiceDep,
) -> SessionList:
    """
    **protected**
    Retrieves all active sessions for the authenticated user.
    The provided access token must be valid.
    """
    return await auth_service.list_sessions(
        user_id=access_token.sub, current_session_id=access_token.sid
    )


@auth_router.get('/sessions/{user_id}/', dependencies=[Depends(AuthorizedAdmin)])
async def list_user_sessions(
    user_id: Annotated[str, Path(...)],
    auth_service: AuthServiceDep,
) -> SessionList:
    """
    **admin protected**
    Retrieves all active sessions for a specified user.
    """
    return await auth_service.list_sessions(user_id=user_id, current_session_id=None)
