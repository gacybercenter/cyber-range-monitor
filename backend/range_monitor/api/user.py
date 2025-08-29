from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Query, status

from range_monitor.params import PageParams, TimestampParams
from range_monitor.users.depends import (
    AuthorizationDep,
    AuthServiceDep,
    RoleRequired,
    SessionServiceDep,
    UserServiceDep,
)
from range_monitor.users.roles import UserRoles
from range_monitor.users.schema import (
    CreateUserBody,
    UpdateUserBody,
    UserID,
    UserPageList,
    UserSchema,
)
from range_monitor.users.sessions.schema import UserSessionList
from range_monitor.utils.openapi_extra import api_error

users_router = APIRouter(
    dependencies=[
        Depends(RoleRequired(UserRoles.ADMIN))
    ],
)

UserPathID = Annotated[
    UserID,
    Path(
        ...,
        description='The unique identifier of the user',
        min_length=1,
        max_length=64,
    ),
]

@users_router.get('/', response_model=UserPageList)
async def list_users(
    user_service: UserServiceDep,
    timestamp_params: Annotated[TimestampParams, Depends(TimestampParams.depends)],
    page_params: Annotated[PageParams, Depends(PageParams.depends)],
    with_role: Annotated[UserRoles | None, Query(description='Filter by role')] = None,
) -> UserPageList:
    """
    Lists users with optional filtering and pagination.
    """
    return await user_service.paginate_users(
        page=page_params,
        timestamps=timestamp_params,
        with_role=with_role,
    )


@users_router.post('/', response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: Annotated[CreateUserBody, Body(...)],
    user_service: UserServiceDep,
) -> UserSchema:
    """
    Creates a new user.
    """
    new_user = await user_service.create_user(params=body)
    return UserSchema.convert(new_user)


@users_router.get('/{user_id}/')
async def get_user(user_id: UserPathID, user_service: UserServiceDep) -> UserSchema:
    """
    Retrieves a user by their unique identifier.
    """
    return await user_service.read(user_id)

@users_router.delete('/{user_id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UserPathID,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    actor: UserSchema = Depends(RoleRequired(UserRoles.ADMIN)),
) -> None:
    """
    Deletes a user and removes all of their sessions.
    """
    await user_service.delete_user_id(user_id, actor.id)
    await auth_service.remove_all_sessions(user_id)


@users_router.patch(
    '/{user_id}/',
    response_model=UserSchema,
    status_code=status.HTTP_202_ACCEPTED
)
async def update_user(
    user_id: UserPathID,
    body: UpdateUserBody,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
) -> UserSchema:
    """
    Updates a user, if the password is updated all existing sessions
    will be invalidated.
    """
    new_user = await user_service.update_user_id(user_id=user_id, params=body)
    if body.password is not None:
        await auth_service.remove_all_sessions(user_id)
    return new_user


@users_router.get(
    '/{user_id}/sessions/',
    response_model=UserSessionList
)
async def list_user_sessions(
    user_id: UserPathID,
    session_manager: SessionServiceDep,
) -> UserSessionList:
    """
    Lists all active sessions for a given user.
    """
    return await session_manager.list_user_sessions(user_id)

@users_router.delete(
    '/sessions/{session_id}/',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Session not found'),
        status.HTTP_400_BAD_REQUEST: api_error('Just logout, instead'),
        status.HTTP_422_UNPROCESSABLE_ENTITY: api_error('Invalid session ID')
    },
)
async def delete_user_session(
    session_id: Annotated[str, Path(
        ...,
        min_length=1,
        max_length=255,
        description='The session ID to delete',
    )],
    session_manager: SessionServiceDep,
    authorization: AuthorizationDep
) -> None:
    """
    Deletes a specific session for a given user.
    """
    # should always be admin, but just in case
    await session_manager.delete_session_by_id(
        current_user_id=authorization['user'].id,
        current_session_id=authorization['session'].session_id,
        session_id=session_id,
        is_admin=(authorization['user'].role == UserRoles.ADMIN),
    )