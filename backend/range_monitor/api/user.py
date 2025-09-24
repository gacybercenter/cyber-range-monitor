from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.auth.depends import (
    AdminRoleDep,
    AdminRoleRequired,
    GuestRoleDep,
    TokenServiceDep,
    UserRoleDep,
    UserServiceDep,
)
from range_monitor.auth.schema import (
    UserCreateBody,
    UserID,
    UserPage,
    UserPatchBody,
    UserPatchProfile,
    UserQuery,
    UserSchema,
)
from range_monitor.params import PageParamsDep, TimestampParamsDep
from range_monitor.utils.openapi_extra import api_error

users_router = APIRouter()


UserIdPathParam = Annotated[
    UserID,
    Path(
        ...,
        description='The unique identifier of the user.',
        min_length=1,
        max_length=64,
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
async def update_user_profile(
    user_claim: UserRoleDep,
    body: Annotated[UserPatchProfile, Body(...)],
    user_service: UserServiceDep,
    tokens: TokenServiceDep,
) -> UserSchema:
    '''
    **User Role Required**
    Updates the profile of the currently authenticated user.
    '''
    async with tokens.blacklist_on_error(user_claim):
        updated = await user_service.patch_user(
            user_id=user_claim.sub,
            params=body,
        )

    if body.password is not None:
        await tokens.claims.incr_cver(user_claim.sub)

    return updated


@users_router.get(
    '/profile/',
    response_model=UserSchema
)
async def get_user_profile(
    user_claim: GuestRoleDep,
    user_service: UserServiceDep,
    tokens: TokenServiceDep,
) -> UserSchema:
    '''
    **Guest Role Required**
    Retrieves the profile of the currently authenticated user.
    '''
    async with tokens.blacklist_on_error(user_claim):
        return await user_service.read_user(user_claim.sub)


@users_router.get(
    '/',
    response_model=UserPage,
    dependencies=[
        Depends(AdminRoleRequired)
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
    }
)
async def list_users(
    user_service: UserServiceDep,
    timestamps: TimestampParamsDep,
    page: PageParamsDep,
    filters: Annotated[UserQuery, Query(
        description='Optional filters to apply to the user list.'
    )]
) -> UserPage:
    '''
    **Admin Role Required**
    Lists users with optional filtering and pagination.
    '''
    return await user_service.list_users_by(
        page=page,
        timestamps=timestamps,
        filters=filters,
    )



@users_router.get(
    '/{user_id}/',
    response_model=UserSchema,
    dependencies=[
        Depends(AdminRoleRequired)
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def read_user(
    user_id: UserIdPathParam,
    user_service: UserServiceDep,
) -> UserSchema:
    """
    **Admin Role Required**
    Retrieves a user by their unique ID.
    """
    return await user_service.read_user(user_id)


@users_router.post(
    '/',
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(AdminRoleRequired)
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_409_CONFLICT: api_error('Username already exists.'),
    }
)
async def create_user(
    body: Annotated[UserCreateBody, Body(...)],
    user_service: UserServiceDep,
) -> UserSchema:
    """
    **Admin Role Required**
    Creates a new user.
    """
    return await user_service.create_user(params=body)


@users_router.delete(
    '/{user_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(AdminRoleRequired)
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error(
            'User is not an admin or tries delete self'
        ),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def delete_user(
    user_id: UserIdPathParam,
    user_service: UserServiceDep,
    actor: AdminRoleDep,
    token_service: TokenServiceDep,
) -> None:
    """
    **Admin Role Required**
    Deletes a user and removes all of their sessions.
    """
    await user_service.delete_by_id(
        user_id=user_id,
        actor_id=actor.sub
    )
    # lazy delete all tokens/sessions for the user
    await token_service.claims.incr_cver(user_id)


@users_router.patch(
    '/{user_id}/',
    response_model=UserSchema,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[
        Depends(AdminRoleRequired)
    ],
    responses={
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: api_error('User ID provided does not exist.'),
    }
)
async def update_user(
    user_id: UserIdPathParam,
    body: Annotated[UserPatchBody, Body(...)],
    user_service: UserServiceDep,
    token_service: TokenServiceDep,
) -> UserSchema:
    """
    **Admin Role Required**
    Updates a user's information.
    """
    updated = await user_service.patch_user(
        user_id=user_id,
        params=body,
    )
    if body.password or body.role:
        await token_service.claims.incr_cver(user_id)
    return updated
