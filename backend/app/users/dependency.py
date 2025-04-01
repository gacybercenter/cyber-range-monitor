from typing import Annotated

from fastapi import Depends, Security

from app.core.dependency import DatabaseDep

from .model import Role, User
from .errors import RoleNotAllowed, UserSessionInvalid
from app.auth.dependency import AuthenticationDep, APIKeyData
from .service import UserService


async def get_user_service(db: DatabaseDep) -> UserService:
    '''creates the user service with the DB dependency

    Arguments:
        db {DatabaseDep} -- the DB dependency

    Returns:
        UserService -- the user service
    '''
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def key_to_user(
    key_data: APIKeyData,
    user_controller: UserService
) -> User:
    '''Converts the APIKeyData into an AuthenticationDep object
    which is used to authenticate the user

    Arguments:
        key_data {APIKeyData} -- the APIKeyData object
        user_controller {UserServiceDep} -- the user controller
    Returns:
        AuthenticationDep -- the authentication dependency
    '''
    existing_user = await user_controller.get_username(
        key_data.identity.username
    )
    if not existing_user:
        raise UserSessionInvalid()
    return existing_user


async def get_current_user(
    key_data: AuthenticationDep,
    user_controller: UserServiceDep
) -> User:
    '''Retrieves the current user from the database and performs
    sanity checks to ensure the user is valid and still exists
    '''
    user = await key_to_user(key_data, user_controller)
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]


def role_checker(min_role: Role):
    '''returns a factory function that checks if the current user's role
    is greater than or equal to the minimum role required
    Arguments:
        min_role {Role} -- the minimum role required to access the route
    '''
    async def role_allowed(current_user: CurrentUserDep) -> User:
        if current_user.role < min_role:
            raise RoleNotAllowed()
        return current_user

    return role_allowed


RoleRequired = role_checker(Role.READ_ONLY)
UserRequired = role_checker(Role.USER)
AdminRequired = role_checker(Role.ADMIN)

AnyRoleDep = Annotated[User, Security(RoleRequired)]
UserRoleDep = Annotated[User, Security(UserRequired)]
AdminRoleDep = Annotated[User, Security(AdminRequired)]
