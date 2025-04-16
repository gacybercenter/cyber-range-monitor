from typing import Annotated

from fastapi import Depends, Security

from app.core.dependency import DatabaseDep


from app.auth.dependency import (
    AuthenticationDep,
    APIKeyData,
    KeyServiceDep,
    validate_api_key,
    ClientIdentityDep,
    KeyBearerSecurityDep
)
from .service import UserService
from .model import Role, User
from .errors import RoleNotAllowed, UserSessionInvalid
from .schema import AuthContext, KeyContext


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


async def get_auth_context(
    client: ClientIdentityDep,
    api_key: KeyBearerSecurityDep,
    user_controller: UserServiceDep,
    key_service: KeyServiceDep
) -> AuthContext:
    '''re runs all of the logic for authentication with both the auth dependency 
    function running and user function and then uses key service to get the keys 
    health. contains alot of dependencies to ensure that only one of each instance such
    as a database session is created on each request, however has the downside of being
    a little more verbose
    '''
    key_contents = await validate_api_key(api_key, client, key_service)  # method for first auth dependency
    # second method for auth
    user = await key_to_user(key_contents, user_controller)

    key = api_key.credentials

    key_health = await key_service.inspect_key_health(key_contents, key)

    auth = {
        **key_health.serialize(),
        'api_key': key
    }

    return AuthContext(
        user=user_controller.serialize(user),
        auth=KeyContext(**auth)
    )

AuthContextDep = Annotated[AuthContext, Depends(get_auth_context)]


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
