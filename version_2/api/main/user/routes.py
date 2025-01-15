from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, dependencies, status, Body, Response, Request
from httpx import request
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import (
    OAuth2PasswordRequestForm
)

from api.config.settings import app_config
from api.main.schemas.user import CreateUser, UpdateUser, UserResponse
from api.main.user.services import UserService
from api.utils.dependencies import needs_db
from api.utils.errors import HTTPUnauthorizedToken, ResourceNotFound
from api.utils.security.auth import (
    JWTService,
    TokenTypes,
    UserOAuthData,
    EncodedToken,
    admin_required,
    get_current_user,
    require_auth
)
from api.utils.errors import ResourceNotFound
from api.models.user import UserRoles


user_service = UserService()

# ==================
#     User Auth
# ==================

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


@auth_router.post('/refresh', response_model=EncodedToken)
async def refresh_token(request: Request, response: Response) -> EncodedToken:

    encoded_token = request.cookies.get('refresh_token')
    if not encoded_token:
        raise HTTPUnauthorizedToken()

    decoded_token = await JWTService.get_refresh_token(encoded_token)
    if JWTService.has_revoked(decoded_token.jti):
        raise HTTPUnauthorizedToken()

    _, encoded_access = await JWTService.create_token(
        decoded_token.sub, decoded_token.role, TokenTypes.ACCESS
    )

    _, encoded_refresh = await JWTService.create_token(
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
    response: Response
) -> dict:
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        raise HTTPUnauthorizedToken()

    decoded_refresh = await JWTService.get_refresh_token(refresh_token)
    await JWTService.revoke(decoded_refresh.jti, refresh_token)
    response.delete_cookie('refresh_token')

    access_token = request.headers.get("Authorization")
    if access_token and access_token.startswith("Bearer "):
        access_token = access_token.split(" ")[1]
        decoded_access = await JWTService.decode_access_token(access_token)
        await JWTService.revoke(decoded_access.jti, access_token)

    return {'detail': 'Successfully logged out'}

# ==================
#     User CRUD
# ==================
user_router = APIRouter(
    prefix='/user',
    tags=['User']
)


@user_router.post(
    '/', 
    response_model=UserResponse, 
    dependencies=[Depends(admin_required)], 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    create_req: CreateUser,
    db: needs_db,
) -> UserResponse:
    '''
    creates a user given the request body schema
    Arguments:
        create_schema {CreateUser} -- the request body schema
    Keyword Arguments:
        db {AsyncSession} - default: {Depends(get_db)})
    Raises:
        HTTPException: 400 - Username is already taken
    Returns:
        UserResponse -- the created user
    '''
    username_taken = await user_service.username_exists(
        db,
        create_req.username
    )
    if username_taken:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Username is already taken'
        )

    resulting_user = await user_service.create_user(db, create_req)
    return resulting_user  # type: ignore


@user_router.put('/{user_id}', response_model=UserResponse)
async def update_user(
    user_id: int,
    update_req: UpdateUser,
    db: needs_db,
    current_user: UserOAuthData = Depends(get_current_user)
) -> UserResponse:
    '''
    updates the user given an id and uses the schema to update the user's data

    Arguments:
        user_id {int} -- user id
        update_schema {UpdateUser} -- the request body schema
    Keyword Arguments:
        db {AsyncSession} -- (default: {Depends(get_db)})
    Returns:
        UserResponse
    '''
    acting_user = await user_service.get_username(current_user.sub, db)
    if acting_user is None:
        raise ResourceNotFound('User')

    if (
        acting_user.id != user_id and
        acting_user.role != UserRoles.admin.value
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You do not have permission to update this user'
        )

    updated_data = await user_service.update_user(db, user_id, update_req)
    return updated_data  # type: ignore


@user_router.delete('/{user_id}')
async def delete_user(user_id: int, db: needs_db) -> dict:
    # Depends(admin_required)
    await user_service.delete_user(db, user_id)
    return {'detail': 'User deleted successfully'}


@user_router.get('/{user_id}', response_model=UserResponse, dependencies=[Depends(require_auth)])
async def read_user(user_id: int, db: needs_db) -> UserResponse:
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return user  # type: ignore


@user_router.get('/', response_model=list[UserResponse])
async def read_all_users(db: needs_db) -> list[UserResponse]:
    users = await user_service.get_all(db)
    return users  # type: ignore
