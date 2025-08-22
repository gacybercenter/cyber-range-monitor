from uuid import UUID

from app.api.http_exceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound
from app.security import passwords

from ..auth import service as auth_service
from ..auth.repo import SessionRepo
from .model import User
from .repo import RoleRepo, UserRepo
from .schema import (
    CreateUserSchema,
    RoleSchema,
    UpdateUserSchema,
    UserAuthSchema,
    UserSchema,
)


async def get_user_id(user_id: UUID, users: UserRepo) -> User:
    '''Retrieve a user by their ID.'''
    if not (user := await users.get_by_id(user_id)):
        raise HTTPNotFound('User')
    return user

async def create_user(
    params: CreateUserSchema,
    repo: UserRepo
) -> UserSchema:
    '''
    Create a new user with the provided parameters.

    Parameters
    ----------
    params : CreateUserSchema
    repo : UserRepo

    Returns
    -------
    UserSchema

    Raises
    ------
    HTTPBadRequest
        _User name is taken or invalid user role_
    '''
    if await repo.username_taken(params.username):
        raise HTTPBadRequest('Username is already taken.')

    password_hash = passwords.hash_password(params.password)
    args = params.dump_exclude({'password'})
    args['password_hash'] = password_hash
    new_user = await repo.create_user(**args)
    if not new_user:
        raise HTTPBadRequest('Invalid role provided.')

    return UserSchema(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role.name,
        is_active=new_user.is_active
    )



async def update_user(
    user_id: UUID,
    params: UpdateUserSchema,
    users: UserRepo
) -> UserSchema:
    '''
    Update an existing user with the provided parameters.

    Parameters
    ----------
    user_id : UUID
    params : UpdateUserSchema
    repo : UserRepo

    Returns
    -------
    UserSchema

    Raises
    ------
    HTTPBadRequest
        _Username is taken or no valid fields to update_
    HTTPNotFound
        _User not found or invalid role provided_
    '''
    existing_user = await get_user_id(user_id, users)
    if params.username and params.username != existing_user.username:
        if await users.username_taken(params.username):
            raise HTTPBadRequest('Username is already taken.')

    update_args = params.dump()
    if not update_args:
        raise HTTPBadRequest('No valid fields to update.')

    if (password := update_args.pop('password', None)):
        update_args['password_hash'] = passwords.hash_password(password)

    updated_user = await users.update_user(
        existing_user,
        params=update_args
    )
    if not updated_user:
        raise HTTPBadRequest('Invalid role provided.')

    return UserSchema(
        id=updated_user.id,
        username=updated_user.username,
        role=updated_user.role.name,
        is_active=updated_user.is_active
    )

async def delete_user(user_id: UUID, users: UserRepo, sessions: SessionRepo) -> None:
    '''
    Delete a user by their ID.


    Raises
    ------
    HTTPNotFound
        _User not found_
    HTTPBadRequest
        _Failed to delete user._
    '''
    user = await get_user_id(user_id, users)
    if not await users.delete_user(user):
        raise HTTPBadRequest('Failed to delete user.')
    await sessions.remove_all(user_id=str(user.id))

def parse_role_scopes(scopes_str: str) -> list[str]:
    return [
        scope.strip() for scope in scopes_str.split(',')
        if scope.strip()
    ]

async def authenticate_user(
    username: str,
    password: str,
    repo: UserRepo
) -> UserAuthSchema:
    if not (user := await repo.get_by_username(username)):
        raise HTTPBadRequest('Invalid username or password.')

    if not passwords.check_password(
        plain_password=password,
        stored_hash=user.password_hash
    ):
        raise HTTPBadRequest('Invalid password.')

    return UserAuthSchema(
        username=user.username,
        id=user.id,
        role=user.role.name,
        scopes=parse_role_scopes(user.role.scopes_json)
    )

async def reader_user_id(user_id: UUID, repo: UserRepo) -> UserSchema:
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPBadRequest('User not found.')

    return UserSchema(
        id=user.id,
        username=user.username,
        role=user.role.name,
        is_active=user.is_active
    )


async def get_role_details(role_name: str, roles: RoleRepo) -> RoleSchema:
    if not (role := await roles.get_by_name(role_name)):
        raise HTTPNotFound('Role')

    scopes = parse_role_scopes(role.scopes_json)
    return RoleSchema(
        id=role.id,
        name=role.name,
        description=role.description or 'No description provided.',
        scopes=scopes
    )

async def load_current_user(
    signed_session_id: str,
    users: UserRepo,
    sessions: SessionRepo
) -> UserSchema:
    session_payload = await auth_service.load_session(
        signed_session_id,
        sessions
    )
    if not session_payload:
        raise HTTPForbidden('Invalid or expired session.')

    user = await users.get_by_id(
        UUID(session_payload.user_id)
    )

    if not user:
        raise HTTPNotFound('User')

    return UserSchema(
        id=user.id,
        username=user.username,
        role=user.role.name,
        is_active=user.is_active
    )



