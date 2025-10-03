from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.auth.depends import (
    AdminClaimDep,
    AdminRequired,
    AuthRepoDep,
    GuestClaimDep,
    UserClaimDep,
)
from range_monitor.schema.params import PageParamsDep
from range_monitor.users.depends import UsersServiceDep
from range_monitor.users.schema import (
    UserCreateBody,
    UserID,
    UserPage,
    UserPatchBody,
    UserPatchProfile,
    UserQuery,
    UserSchema,
)
from range_monitor.utils.openapi_extra import api_error

users_router = APIRouter()

UserPath = Annotated[
    UserID,
    Path(
        ...,
        description='The unique identifier of the user.',
    )
]

@users_router.patch(
    '/profile/',
    response_model=UserSchema,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Unauthenticated request'),
        status.HTTP_403_FORBIDDEN: api_error('Insufficient role to access this resource'),
    }
)
async def update_profile(
    current_user: UserClaimDep,
    body: Annotated[UserPatchProfile, Body(...)],
    auth_repo: AuthRepoDep,
    user_service: UsersServiceDep,
) -> UserSchema:
    '''
    **User Role Required**
    Updates the profile of the currently authenticated user.
    '''
    updated = await user_service.edit_user(
        user_id=current_user.sub,
        params=body,
    )
    await auth_repo.set_cver(
        str(updated.id),
        updated.credential_version
    )
    return updated


@users_router.get('/profile/', response_model=UserSchema)
async def read_user_profile(
    current_user: GuestClaimDep,
    user_service: UsersServiceDep,
) -> UserSchema:
    '''
    **Guest Role Required**
    Retrieves the profile of the currently authenticated user.
    '''
    return await user_service.read_user(user_id=current_user.user_id)



@users_router.get(
    '/',
    response_model=UserPage,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
    }
)
async def list_users(
    user_service: UsersServiceDep,
    page: PageParamsDep,
    filters: Annotated[UserQuery, Query(
        description='Optional filters to apply to the user list.'
    )]
) -> UserPage:
    '''
    **Admin Role Required**
    Lists users with optional filtering and pagination.
    '''
    return await user_service.list_users(filters, page)



@users_router.get(
    '/{user_id}/',
    response_model=UserSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def read_user(
    user_id: UserPath,
    user_service: UsersServiceDep,
) -> UserSchema:
    '''
    **Admin Role Required**
    Retrieves a user by their unique ID.
    '''
    return await user_service.read_user(user_id)


@users_router.post(
    '/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_409_CONFLICT: api_error('Username already exists.'),
    }
)
async def create_user(
    admin: AdminClaimDep,
    body: Annotated[UserCreateBody, Body(...)],
    user_service: UsersServiceDep,
) -> UserSchema:
    '''
    **User Role Required**
    Creates a new user, if the current user is not admin
    and attempts to create a non-guest user, a ForbiddenError is raised.
    '''
    return await user_service.create_user(
        body=body,
        creator_id=admin.sub
    )


@users_router.delete(
    '/{user_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error(
            'User is not an admin or tries delete self'
        ),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def delete_user(
    user_id: UserPath,
    auth_repo: AuthRepoDep,
    user_service: UsersServiceDep,
    actor: UserClaimDep,
) -> None:
    '''
    **Admin Role Required**
    Deletes a user and lazy deletes the token claims
    '''
    await user_service.delete_user_id(
        user_id=user_id,
        current_user_id=actor.sub
    )
    await auth_repo.incr_cver(str(user_id))


@users_router.patch(
    '/{user_id}/',
    response_model=UserSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AdminRequired)],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def patch_user(
    user_id: UserPath,
    body: Annotated[UserPatchBody, Body()],
    auth_repo: AuthRepoDep,
    user_service: UsersServiceDep,
) -> UserSchema:
    '''
    **Admin Role Required**
    Updates a user's information.
    '''
    response = await user_service.edit_user(
        user_id=user_id,
        params=body,
    )
    await auth_repo.set_cver(
        str(response.id),
        response.credential_version
    )
    return response
