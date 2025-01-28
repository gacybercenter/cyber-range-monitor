from fastapi import APIRouter, Depends, HTTPException, status

from api.models.user import UserRoles
from api.schemas.user_schema import CreateUser, UpdateUser, UserResponse, UserDetailsResponse
from api.services.controller import UserService
from api.core.dependencies import needs_db
from api.core.errors import HTTPNotFound, HTTPForbidden, BadRequest
from api.services.auth import (
    UserOAuthData,
    admin_required,
    require_auth
)
from api.core.errors import HTTPNotFound
from api.models.user import UserRoles


user_service = UserService()
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
async def create_user(create_req: CreateUser, db: needs_db) -> UserResponse:
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
        db, create_req.username
    )
    if username_taken:
        raise BadRequest('Username is already taken')

    resulting_user = await user_service.create_user(db, create_req)
    return resulting_user  # type: ignore


@user_router.put('/{user_id}', response_model=UserResponse, dependencies=[Depends(admin_required)])
async def update_user(
    user_id: int,
    update_req: UpdateUser,
    db: needs_db
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
    updated_data = await user_service.update_user(db, user_id, update_req)
    return updated_data  # type: ignore


@user_router.delete('/{user_id}')
async def delete_user(
    user_id: int,
    db: needs_db,
    admin_user: UserOAuthData = Depends(admin_required)
) -> dict:
    await user_service.delete_user(db, user_id, admin_user.sub)
    return {'detail': 'User deleted successfully'}


@user_router.get('/{user_id}', response_model=UserResponse)
async def read_user(
    user_id: int,
    db: needs_db,
    reader: UserOAuthData = Depends(require_auth)
) -> UserResponse:
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')

    if not UserRoles(reader.role) >= UserRoles(user.role):
        raise HTTPForbidden('Cannot read a user with higher permissions')

    return user  # type: ignore


@user_router.get('/', response_model=list[UserResponse])
async def read_all_users(
    db: needs_db,
    reader: UserOAuthData = Depends(require_auth)
) -> list[UserResponse]:
    users = await user_service.role_based_read_all(reader.role, db)
    return users  # type: ignore


@user_router.get('/details', dependencies=[Depends(admin_required)], response_model=UserDetailsResponse)
async def read_all_user_details(db: needs_db) -> list[UserDetailsResponse]:
    users = await user_service.get_all(db)
    return users  # type: ignore


@user_router.get('/details/{user_id}', dependencies=[Depends(admin_required)], response_model=UserDetailsResponse)
async def read_user_details(user_id: int, db: needs_db) -> UserDetailsResponse:
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise HTTPNotFound('User')
    return user  # type: ignore
