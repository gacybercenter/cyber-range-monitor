from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from fastapi.security import OAuth2PasswordRequestForm

from api.db.logging import LogWriter
from api.config.settings import app_config
from api.main.services.user_service import UserService
from api.utils.dependencies import needs_db
from api.utils.errors import HTTPUnauthorizedToken
from api.utils.security.auth import (
    JWTService,
    TokenTypes,
    UserOAuthData,
    EncodedToken,
    token_required
)
from api.utils.generics import ResponseMessage

logger = LogWriter('JWT/AUTH')

user_service = UserService()

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
)


@auth_router.post('/token', response_model=EncodedToken)
async def login_user(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: needs_db
) -> EncodedToken:
    await logger.info(f'User {form_data.username} is attempting to login...', db)
    user = await user_service.verify_credentials(
        form_data.username,
        form_data.password,
        db
    )

    if not user:
        await logger.error(f'User {form_data.username} failed to login', db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password, please try again'
        )

    encoded_access = await JWTService.create_token(
        user.username, user.role, TokenTypes.ACCESS  # type: ignore
    )

    encoded_refresh = await JWTService.create_token(
        user.username, user.role, TokenTypes.REFRESH   # type: ignore
    )

    # NOTE: IN PRODUCTION UNCOMMENT THE COMMENTED LINES
    response.set_cookie(
        key='refresh_token',
        value=encoded_refresh,
        # httponly=True,
        max_age=app_config.REFRESH_TOKEN_EXP_SEC,
        expires=app_config.REFRESH_TOKEN_EXP_SEC,
        # secure=True,
        samesite='strict'
    )
    logger.debug(f'User {form_data.username} successfully logged in')
    return EncodedToken(access_token=encoded_access)


@auth_router.post('/refresh', response_model=EncodedToken)
async def refresh_access_token(
    request: Request,
    response: Response,
    token: token_required,
    db: needs_db
) -> EncodedToken:
    '''
    Refreshes the access token using the refresh token stored in the cookies
    from the request. The access token from the Authorization header is used
    to handle instances where the route maybe called before it expires, so
    it can be revoked before creating a new one.
    Arguments:
        request {Request}  
        response {Response} 
    Raises:
        HTTPUnauthorizedToken: if the refresh token is not found in the cookies or has been revoked

    Returns:
        EncodedToken -- the encoded access token
    '''
    await logger.info('The user is attempting to refresh their access token...', db)
    try:
        decoded_access = await JWTService.decode_access_token(token)
        await JWTService.revoke(decoded_access.jti, token)
    except Exception:
        pass  # if the server fails to decode the acess token, it has expired

    encoded_token = request.cookies.get('refresh_token')
    if not encoded_token:
        await logger.warning('No refresh token was found in the clients cookies', db)
        raise HTTPUnauthorizedToken()

    decoded_token = await JWTService.get_refresh_token(encoded_token)
    if JWTService.has_revoked(decoded_token.jti):
        await logger.warning(
            'The client has attempted to use a refresh token that the sever has revoked', db
        )
        raise HTTPUnauthorizedToken()

    logger.debug('Creating a token pair (access/refresh) for the client.')
    encoded_access = await JWTService.create_token(
        decoded_token.sub,
        decoded_token.role,
        TokenTypes.ACCESS
    )

    encoded_refresh = await JWTService.create_token(
        decoded_token.sub,
        decoded_token.role,
        TokenTypes.REFRESH
    )
    # NOTE: IN PRODUCTION UNCOMMENT THE COMMENTED LINES
    response.set_cookie(
        key='refresh_token',
        value=encoded_refresh,
        # httponly=True,
        max_age=app_config.REFRESH_TOKEN_EXP_SEC,
        expires=app_config.REFRESH_TOKEN_EXP_SEC,
        # secure=True,
        samesite='strict'
    )
    await logger.info(f'"{decoded_token.sub}" has refreshed their access token.', db)
    return EncodedToken(access_token=encoded_access)


@auth_router.get('/logout', response_model=ResponseMessage)
async def logout_user(
    request: Request,
    response: Response,
    token: token_required,
    db: needs_db
) -> ResponseMessage:
    '''
    Logs out the user by revoking the refresh token stored in the cookies
    and the access token in the Authorization header if it exists.

    Arguments:
        request {Request}  
        response {Response} 
        token - encoded access token
    Raises:
        HTTPUnauthorizedToken: _description_

    Returns:
        dict 
    '''
    await logger.info('A user is attempting to logout...', db)
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        await logger.warning('An unauthorized client has tried to logout', db)
        raise HTTPUnauthorizedToken()

    decoded_refresh = await JWTService.get_refresh_token(refresh_token)
    await JWTService.revoke(decoded_refresh.jti, refresh_token)
    response.delete_cookie('refresh_token')
    await logger.info(
        f'"{decoded_refresh.sub}" has logged out and their access token has been revoked.',
        db
    )
    try:
        decoded_access = await JWTService.decode_access_token(token)
        await JWTService.revoke(decoded_access.jti, token)
    except Exception:
        pass

    return ResponseMessage(message='User has been logged out')
