from typing import Annotated

from fastapi import Depends

from app.core.dependency import DatabaseDep

from .model import Role, User
from .errors import UserSessionInvalid
from ..auth.dependency import AuthDep
from .service import UserService


async def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)



UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    user_identity: AuthDep, 
    user_controller: UserServiceDep
) -> User:
    '''Retrieves the current user from the database and performs
    sanity checks to ensure the user is valid and the client
    identity is the same as the user's mapped user

    Arguments:
        user_identity {AuthDep} -- _description_
        user_controller {UserServiceDep} -- _description_
    Raises:
        UserSessionInvalid: the user is invalid or the client identity is not the same 
        as the user's mapped user
    Returns:
        User -- the user corresponding to the client identity
    '''
    existing_user = await user_controller.get_username(user_identity.username)
    if not existing_user:
        raise UserSessionInvalid()
    mapped_user = user_identity.client_identity.mapped_user
    if mapped_user != "Unknown" and existing_user.username != mapped_user:
        raise UserSessionInvalid()
    return existing_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def role_checker(min_role: Role):
    '''returns a factory function that checks if the current user's role
    is greater than or equal to the minimum role required
    Arguments:
        min_role {Role} -- the minimum role required to access the route
    '''
    async def role_allowed(current_user: CurrentUserDep) -> User:
        if current_user.role < min_role:
            raise UserSessionInvalid()
        return current_user

    return role_allowed


RoleRequired = role_checker(Role.READ_ONLY)
UserRequired = role_checker(Role.USER)
AdminRequired = role_checker(Role.ADMIN)

AnyRoleDep = Annotated[User, Depends(RoleRequired)]
UserRoleDep = Annotated[User, Depends(UserRequired)]
AdminRoleDep = Annotated[User, Depends(AdminRequired)]
