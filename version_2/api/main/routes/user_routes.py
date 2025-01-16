from os import read
from fastapi import APIRouter, Depends, HTTPException, status

from api.models.user import UserRoles
from api.main.schemas.user import CreateUser, UpdateUser, UserResponse, UserDetailsResponse
from api.main.services.user_service import UserService
from api.utils.dependencies import needs_db
from api.utils.errors import ResourceNotFound, ForbiddenAction
from api.utils.security.auth import (
    UserOAuthData,
    admin_required,
    get_current_user,
    require_auth,
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

    not_admin = (acting_user.role != UserRoles.admin.value)

    if acting_user.id != user_id and not_admin:
        raise ForbiddenAction()

    if update_req.role is not None and not_admin:
        raise ForbiddenAction()

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
        raise ResourceNotFound('User')

    if not UserRoles(reader.role) >= UserRoles(user.role):
        raise ForbiddenAction('Cannot read a user with higher permissions')

    return user  # type: ignore


@user_router.get('/', response_model=list[UserResponse])
async def read_all_users(
    db: needs_db,
    reader: UserOAuthData = Depends(require_auth)
) -> list[UserResponse]:
    users = await user_service.role_based_read_all(reader.role, db)
    return users  # type: ignore


@user_router.get(
    '/details',
    dependencies=[Depends(admin_required)], 
    response_model=UserDetailsResponse
)
async def read_all_user_details(db: needs_db) -> list[UserDetailsResponse]:
    users = await user_service.get_all(db)
    return users # type: ignore


@user_router.get(
    '/details/{user_id}',
    dependencies=[Depends(admin_required)],
    response_model=UserDetailsResponse
)
async def read_user_details(
    user_id: int,
    db: needs_db
) -> UserDetailsResponse:
    user = await user_service.get_by_id(user_id, db)
    if not user:
        raise ResourceNotFound('User')

    return user  # type: ignore

