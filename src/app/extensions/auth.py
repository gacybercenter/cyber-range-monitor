# 'Role Based Authentication / Authorization Control'
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.common.errors import HTTPUnauthorized
from app.sessions.constant import SESSION_AUTHORITY
from app.sessions.schemas import SessionData
from app.db import get_db
from app.users.models import User, Role
from app.users.service import UserService

user_service = UserService()


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    session_data: SessionData = Depends(SESSION_AUTHORITY)
) -> User:

    existing_user = await user_service.get_username(session_data.username, db)
    if not existing_user:
        raise HTTPUnauthorized(
            'Your session corresponds to a non-existent user, please login again'
        )

    mapped_user = session_data.client_identity.mapped_user
    if mapped_user != 'Unknown' and mapped_user != existing_user.username:
        raise HTTPUnauthorized(
            'Your session is not authorized under your current user.'
        )

    return existing_user


class RoleChecker:
    '''A class based dependency that checks the role of the current user'''

    def __init__(self, min_role: Role) -> None:
        self.min_role = min_role

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role < self.min_role:
            raise HTTPUnauthorized(
                'You do not have the required permissions to access this resource'
            )
        return current_user


class AdminProtected(RoleChecker):
    '''Requires a user to be an Admin'''

    def __init__(self) -> None:
        super().__init__(Role.ADMIN)


class UserProtected(RoleChecker):
    '''Requires a user to be a User (lol)'''

    def __init__(self) -> None:
        super().__init__(Role.USER)


class RoleProtected(RoleChecker):
    '''Any role is allowed'''

    def __init__(self) -> None:
        super().__init__(Role.READ_ONLY)
