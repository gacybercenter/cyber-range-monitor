from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from fastapi.security import OAuth2PasswordRequestForm

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
    user = await user_service.verify_credentials(
        form_data.username,
        form_data.password,
        db
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password, please try again'
        )

    _, encoded_access = await JWTService.create_token(
        user.username, user.role, TokenTypes.ACCESS  # type: ignore
    )

    _, encoded_refresh = await JWTService.create_token(
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

    return EncodedToken(access_token=encoded_access)


@auth_router.get('/check-token', response_model=UserOAuthData)
async def inspect_token(
    token: token_required,
):
    try:
        payload = await JWTService.decode_access_token(token)
        return {
            'valid': True,
            'sub': payload.sub,
            'role': payload.role
        }
    except HTTPUnauthorizedToken as e:
        return {
            'valid': False,
            'detail': e.detail
        }


@auth_router.post('/refresh', response_model=EncodedToken)
async def refresh_access_token(
    request: Request,
    response: Response,
    token: token_required
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

    try:
        decoded_access = await JWTService.decode_access_token(token)
        await JWTService.revoke(decoded_access.jti, token)
    except Exception:
        pass

    encoded_token = request.cookies.get('refresh_token')
    if not encoded_token:
        raise HTTPUnauthorizedToken()

    decoded_token = await JWTService.get_refresh_token(encoded_token)
    if JWTService.has_revoked(decoded_token.jti):
        raise HTTPUnauthorizedToken()

    encoded_access = await JWTService.create_token(
        decoded_token.sub, decoded_token.role, TokenTypes.ACCESS
    )

    encoded_refresh = await JWTService.create_token(
        decoded_token.sub, decoded_token.role, TokenTypes.REFRESH
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

    return EncodedToken(access_token=encoded_access)


@auth_router.get('/logout')
async def logout_user(
    request: Request, 
    response: Response,
    token: token_required
) -> dict:
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
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPUnauthorizedToken()

    decoded_refresh = await JWTService.get_refresh_token(refresh_token)
    await JWTService.revoke(decoded_refresh.jti, refresh_token)
    response.delete_cookie('refresh_token')

    try:
        decoded_access = await JWTService.decode_access_token(token)
        await JWTService.revoke(decoded_access.jti, token)
    except Exception:
        pass
    
    
    return {'detail': 'Successfully logged out'}
