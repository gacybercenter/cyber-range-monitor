
from typing import Annotated

from fastapi import Depends
from app.auth.dependencies import AuthRequired

from app.db.dependencies import DatabaseRequired
from .errors import UserNotAuthorized
from .models import User, Role
from .service import UserService


async def get_user_service(db: DatabaseRequired) -> UserService:
    return UserService(db)

UserController = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    session_data: AuthRequired,
    user_service: UserController
) -> User:
    '''Dependency for resolving the session id into the user sending the request

    Arguments:
        session_data {AuthRequired}
        user_service {UserController}

    Raises:
        UserNotAuthorized:
        UserNotAuthorized:

    Returns:
        User -- the current user
    '''
    existing_user = await user_service.get_username(session_data.username)
    if not existing_user:
        raise UserNotAuthorized(
            'Your session corresponds to a non-existent user, please login again'
        )

    mapped_user = session_data.client_identity.mapped_user
    if mapped_user != 'Unknown' and mapped_user != existing_user.username:
        raise UserNotAuthorized(
            'Your session is not authorized under your current user.'
        )

    return existing_user


CurrentUser = Annotated[User, Depends(get_current_user)]


def role_checker(min_role: Role):
    async def check_role(current_user: CurrentUser) -> User:
        if current_user.role < min_role:
            raise UserNotAuthorized(
                'You do not have the required permissions to access this resource'
            )

        return current_user
    return check_role

AdminProtected = role_checker(Role.ADMIN)
UserProtected = role_checker(Role.USER)
RoleProtected = role_checker(Role.READ_ONLY)

AdminRequired = Annotated[User, Depends(AdminProtected)]
UserRequired = Annotated[User, Depends(UserProtected)]
RoleRequired = Annotated[User, Depends(RoleProtected)]



