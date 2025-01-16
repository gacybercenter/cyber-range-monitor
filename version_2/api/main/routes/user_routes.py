import token
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
from api.main.services.user_service import UserService
from api.utils.dependencies import needs_db
from api.utils.errors import HTTPUnauthorizedToken, ResourceNotFound
from api.utils.security.auth import (
    JWTService,
    TokenTypes,
    UserOAuthData,
    EncodedToken,
    admin_required,
    get_current_user,
    require_auth,
    token_required
)
from api.utils.errors import ResourceNotFound
from api.models.user import UserRoles


user_service = UserService()

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
