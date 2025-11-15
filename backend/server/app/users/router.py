from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status

from server.app.auth.router import AuthorizedAdmin
from server.app.openapi_extra import Error
from server.app.users.depends import AdminRequired, GuestRequired, UsersServiceDep
from server.app.users.schema import (
    CreateUserBody,
    PatchUserBody,
    PatchUserProfile,
    UserID,
    UserPage,
    UserQuery,
    UserSchema,
)
from server.utils.paginate import PageParamsDep

users_router = APIRouter()

UserPath = Annotated[
    UserID,
    Path(
        ...,
        description='The unique identifier of the user.',
    ),
]


@users_router.patch(
    '/profile/',
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Unauthenticated request'),
        status.HTTP_403_FORBIDDEN: Error('Insufficient role to access this resource'),
    },
)
async def patch_user_profile(
    current_user: GuestRequired,
    body: Annotated[PatchUserProfile, Body(...)],
    user_service: UsersServiceDep,
) -> UserSchema:
    """
    **User Role Required**
    Updates the profile of the currently authenticated user.
    If the password changes, the users `credential_version` is incremented.
    Meaning, they must re-authenticate.
    """
    return await user_service.update_user(
        user_id=current_user.id,
        params=body,
    )


@users_router.get('/profile/')
async def get_user_profile(
    current_user: GuestRequired,
    user_service: UsersServiceDep,
) -> UserSchema:
    """
    **Guest Role Required**
    Retrieves the profile of the currently authenticated user.
    """
    return await user_service.get_user(user_id=current_user.id)


@users_router.get(
    '/',
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('User is not an admin.'),
    },
)
async def list_users(
    user_service: UsersServiceDep,
    page: PageParamsDep,
    filters: Annotated[UserQuery, Depends(UserQuery.depends)],
) -> UserPage:
    """
    **Admin Role Required**
    Lists users with optional filtering and pagination.
    """
    return await user_service.list_users(filters, page)


@users_router.get(
    '/{user_id}/',
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: Error('User ID provided does not exist.'),
    },
)
async def get_user(user_id: UserPath, user_service: UsersServiceDep) -> UserSchema:
    """
    **Admin Role Required**
    Retrieves a user by their unique ID.
    """
    return await user_service.get_user(user_id)


@users_router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('User is not an admin.'),
        status.HTTP_409_CONFLICT: Error('Username already exists.'),
    },
)
async def create_user(
    admin: AdminRequired,
    body: Annotated[CreateUserBody, Body(...)],
    user_service: UsersServiceDep,
) -> UserSchema:
    """
    **User Role Required**
    Creates a new user, if the current user is not admin
    and attempts to create a non-guest user, a ForbiddenError is raised.
    """
    return await user_service.create_user(body=body, creator_id=admin.id)


@users_router.delete(
    '/{user_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('User is not an admin or tries delete self'),
        status.HTTP_404_NOT_FOUND: Error('User ID provided does not exist.'),
    },
)
async def delete_user(
    user_id: UserPath,
    user_service: UsersServiceDep,
    actor: AdminRequired,
) -> None:
    """
    **Admin Role Required**
    Deletes a user and lazy deletes the token claims
    by incrementing the `credential_version`.
    """
    await user_service.delete_by_id(
        target_user=user_id,
        current_user=actor.id,
    )


@users_router.patch(
    '/{user_id}/',
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(AuthorizedAdmin)],
    responses={
        status.HTTP_401_UNAUTHORIZED: Error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: Error('User is not an admin.'),
        status.HTTP_404_NOT_FOUND: Error('User ID provided does not exist.'),
    },
)
async def patch_user(
    user_id: UserPath,
    body: Annotated[PatchUserBody, Body()],
    user_service: UsersServiceDep,
) -> UserSchema:
    """
    **Admin Role Required**
    Updates a user's information. If the users
    Role or password changes, the users `credential_version` is
    incremented.
    """
    return await user_service.update_user(user_id=user_id, params=body)
