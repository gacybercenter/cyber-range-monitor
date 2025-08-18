
from fastapi import APIRouter, Depends, status

from app.api.schemas.users import (
    CreateUserRequest,
    DetailedUserPage,
    UpdateUserRequest,
    UserIdPath,
    UserModel,
    UserPage,
    UserQuery,
)

from ..domains.depends import (
    AdminRequired,
    AdminRequiredDep,
    CurrentUserDep,
    UserServiceDep,
    get_current_user,
)
from ..openapi_extra import HTTPError

user_router = APIRouter(dependencies=[Depends(get_current_user)])


@user_router.get('/me', response_model=UserModel)
async def current_user(current_user: CurrentUserDep) -> UserModel:
    return current_user


# /users [Create, Read]
@user_router.post(
    '/',
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_400_BAD_REQUEST: HTTPError('The username is already taken'),
    },
)
async def create_user(
    user_create: CreateUserRequest,
    user_service: UserServiceDep,
) -> UserModel:
    """Create a new user"""
    created_user = await user_service.create_user(create_req=user_create)
    return UserModel.convert(created_user)


@user_router.get(
    '/',
    response_model=UserPage,
)
async def paginate_users(
    params: UserQuery,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserPage:
    return await user_service.get_user_page(
        params=params,
        reader_role=current_user.role,
    )


# /{user_id} [Read, Update, Delete]
@user_router.get('/{user_id}/', response_model=UserModel)
async def get_user(
    user_id: UserIdPath,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserModel:
    """Get a user by ID"""
    return await user_service.get_user(
        user_id=user_id,
        reader_role=current_user.role,
    )


@user_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserIdPath,
    user_service: UserServiceDep,
    current_admin: AdminRequiredDep,
) -> None:
    """Delete a user by ID"""
    await user_service.delete_user(
        user_id=user_id,
        admin_name=current_admin.username,
    )


@user_router.patch('/{user_id}/', response_model=UserModel)
async def update_user(
    user_id: UserIdPath,
    user_update: UpdateUserRequest,
    user_service: UserServiceDep,
    current_user: CurrentUserDep,
) -> UserModel:
    """Update a user by ID"""
    updated_user = await user_service.update_user(
        user_id=user_id,
        update_req=user_update,
        reader_role=current_user.role,
    )
    return UserModel.convert(updated_user)


# /details
@user_router.get(
    '/details/',
    response_model=DetailedUserPage,
    dependencies=[Depends(AdminRequired)],
)
async def paginate_user_details(
    params: UserQuery,
    user_service: UserServiceDep,
) -> DetailedUserPage:
    """Get a paginated list of user details"""
    return await user_service.get_detailed_user_page(params=params)


@user_router.get(
    '/details/{user_id}/',
    response_model=UserModel,
    responses={
        status.HTTP_404_NOT_FOUND: HTTPError('User not found'),
    },
)
async def get_user_details(
    user_id: UserIdPath,
    user_service: UserServiceDep,
) -> UserModel:
    """Get detailed information about a user by ID"""
    return await user_service.get_detailed_user(user_id=user_id)
