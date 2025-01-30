from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request

from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import needs_db, token_required
from app.core import settings
from app.common import LogWriter
from app.services.auth.auth_service import AuthService
from app.services.controller.user_service import UserService


from api.errors import HTTPUnauthorizedToken, HTTPUnauthorized
from app.schemas.auth_schemas import SessionData, UserOAuthData
from app.schemas.generics import ResponseMessage

logger = LogWriter('JWT/AUTH')

user_service = UserService()

auth_router = APIRouter(
    prefix='/auth',
    tags=['Authentication & Authorization']
)

auth_service = AuthService()


@auth_router.post('/token', response_model=JSONResponse)
async def login_user(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: needs_db
) -> JSONResponse:

    await logger.info(f'User {form_data.username} is attempting to login...', db)
    user = await auth_service.authenticate_user(
        form_data.username,
        form_data.password,
        db
    )
    
    if not user:
        await logger.error(f'User {form_data.username} failed to login', db)
        raise HTTPUnauthorized(
            'Invalid username or password, please try again'
        )

    auth_payload = UserOAuthData(
        sub=user.username,  # type: ignore
        role=user.role  # type: ignore
    )

    session_data = await auth_service.create_session(auth_payload)
    auth_payload = session_data.model_dump()
    
    
    response.set_cookie(
        **settings.session_cookie_args(auth_payload['session_id'])
    )
    del auth_payload['session_id']
    logger.debug(f'User {form_data.username} successfully logged in')
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=auth_payload
    )


@auth_router.post('/refresh', response_model=JSONResponse)
async def refresh_session(
    request: Request,
    response: Response,
    token: token_required,
    db: needs_db
) -> JSONResponse:
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
        SessionData -- the encoded access token
    '''
    session_id = request.cookies.get(settings.SESSION_COOKIE)
    if not session_id:
        raise HTTPUnauthorizedToken()
    session_data = await auth_service.refresh_session(session_id, db)
    
    
    
    
    
    
    
    
    
    
    
    
    

@auth_router.post('/logout', response_model=ResponseMessage)
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


@auth_router.post('/revoke', response_model=ResponseMessage)
async def revoke_token(token: str) -> ResponseMessage:
    '''
    Revokes the access token passed in the request body

    Arguments:
        access_token {str} -- the access token to revoke
    '''

    decoded_access = await JWTService.decode_access_token(token)
    await JWTService.revoke(decoded_access.jti, token)

    return ResponseMessage(message='Token has been revoked')
