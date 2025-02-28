from typing import Annotated

from fastapi import Depends

from app.auth.dependency import SessionSecurity
from app.db.dependency import DatabaseRequired
from app.models import Role, User
from app.users.errors import UserSessionInvalid

from .controller import UserService


async def get_user_service(db: DatabaseRequired) -> UserService:
    return UserService(db)

UserController = Annotated[UserService, Depends(get_user_service)]

async def get_current_user(
    session_data: SessionSecurity,
    user_controller: UserController
) -> User:
    existing_user = await user_controller.get_username(session_data.username)
    if not existing_user:
        raise UserSessionInvalid()
    mapped_user = session_data.client_identity.mapped_user
    if mapped_user != 'Unknown' and existing_user.username != mapped_user:
        raise UserSessionInvalid()
    return existing_user
    
CurrentUser = Annotated[User, Depends(get_current_user)]

def role_checker(min_role: Role):
    async def role_allowed(current_user: CurrentUser) -> User:
        if current_user.role < min_role:
            raise UserSessionInvalid()
        return current_user
    return role_allowed
        
RoleProtected = role_checker(Role.READ_ONLY)
UserProtected = role_checker(Role.USER)
AdminProtected = role_checker(Role.ADMIN)

RoleRequired = Annotated[User, Depends(RoleProtected)]
UserRoleRequired = Annotated[User, Depends(UserProtected)]
AdminRequired = Annotated[User, Depends(AdminProtected)]