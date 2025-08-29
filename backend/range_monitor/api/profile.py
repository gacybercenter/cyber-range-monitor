from typing import Annotated

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    status,
)

from range_monitor.users.depends import (
    AuthorizationDep,
    AuthServiceDep,
    RoleRequired,
    SessionServiceDep,
    UserServiceDep,
)
from range_monitor.users.roles import UserRoles
from range_monitor.users.schema import UserSchema, UserUpdateSelfBody
from range_monitor.users.sessions.schema import UserSessionList
from range_monitor.utils.openapi_extra import api_error

profile_router = APIRouter()


@profile_router.get('/', response_model=UserSchema)
async def get_user_profile(authorization: AuthorizationDep) -> UserSchema:
    """
    Retrieves the current authenticated user's information,
    passed via the `Authorization` header.
    """
    return authorization['user']


@profile_router.patch(
    '/', response_model=UserSchema, status_code=status.HTTP_202_ACCEPTED
)
async def update_user_profile(
    user_service: UserServiceDep,
    body: Annotated[UserUpdateSelfBody, Body(...)],
    auth_service: AuthServiceDep,
    current_user: UserSchema = Depends(RoleRequired(UserRoles.USER)),
) -> UserSchema:
    """
    Updates the current authenticated user's information,
    passed via the `Authorization` header.

    If the password is updated, all existing sessions will be
    invalidated through a background task.
    """
    updates = await user_service.update_user_id(user_id=current_user.id, params=body)
    if body.password is not None:
        await auth_service.remove_all_sessions(current_user.id)

    return updates


@profile_router.get('/sessions', response_model=UserSessionList)
async def list_profile_sessions(
    session_manager: SessionServiceDep,
    current_user: UserSchema = Depends(RoleRequired(UserRoles.USER)),
) -> UserSessionList:
    """
    Lists all active sessions for the current authenticated user.
    """
    return await session_manager.list_user_sessions(current_user.id)


@profile_router.delete(
    '/sessions/{session_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_404_NOT_FOUND: api_error('Session not found'),
        status.HTTP_403_FORBIDDEN: api_error('Not authorized to delete this session'),
        status.HTTP_303_SEE_OTHER: api_error('Tries to delete current session.'),
    },
)
async def delete_session_from_profile(
    session_id: Annotated[str, Path(..., min_length=1, max_length=255)],
    session_manager: SessionServiceDep,
    authorization: AuthorizationDep,
) -> None:
    """
    Deletes a specific session by ID for the current authenticated user.
    Note: You cannot delete your current session using this endpoint or
    you will get a 303 See Other response, because why wouldn't you just
    logout.
    """
    if authorization['user'].role < UserRoles.USER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You lack the required permissions to manage your sessions.',
        )

    await session_manager.delete_session_by_id(
        current_user_id=authorization['user'].id,
        current_session_id=authorization['session'].session_id,
        session_id=session_id,
        is_admin=False
    )
