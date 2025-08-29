from typing import Annotated

from fastapi import Depends

from range_monitor.depends import DatabaseDep, PasswordsDep
from range_monitor.errors import ForbiddenAccess
from range_monitor.users.auth import AuthenticationService, Authorization
from range_monitor.users.repo import UserRepo
from range_monitor.users.roles import UserRoles
from range_monitor.users.schema import UserSchema
from range_monitor.users.service import UserService
from range_monitor.users.sessions.depends import SessionSecurity, SessionServiceDep


async def get_user_repo(db: DatabaseDep) -> UserRepo:
    return UserRepo(db)


async def get_user_service(
    passwords: PasswordsDep,
    users: UserRepo = Depends(get_user_repo),
) -> UserService:
    return UserService(users=users, passwords=passwords)


UserRepoDep = Annotated[UserRepo, Depends(get_user_repo)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

async def get_auth_service(
    users: UserRepoDep,
    passwords: PasswordsDep,
    sessions: SessionServiceDep,
) -> AuthenticationService:
    return AuthenticationService(
        users=users,
        passwords=passwords,
        sessions=sessions,
    )

SessionIdRequired = Annotated[str, Depends(SessionSecurity)]
AuthServiceDep = Annotated[AuthenticationService, Depends(get_auth_service)]


async def authorization_required(
    session_id: SessionIdRequired,
    auth_service: AuthServiceDep,
) -> Authorization:
    return await auth_service.get_authorization(session_id)


AuthorizationDep = Annotated[Authorization, Depends(authorization_required)]


class RoleRequired:
    '''
    Dependency class to protect endpoints based on user roles.
    Provide a minimum role and optionally whether to auto-extend
    the idle timeout of the session on each successful request.

    Parameters
    ----------
    min_role : UserRoles
        _The minimum role required to access the endpoint_
    auto_extend_sessions : bool, optional by default True
        _Whether to auto-extend the session idle timeout on each request_

    '''

    def __init__(
        self,
        min_role: UserRoles,
        *,
        auto_extend_sessions: bool = True
    ) -> None:
        self.min_role: UserRoles = min_role
        self.auto_extend_sessions: bool = auto_extend_sessions

    async def __call__(
        self,
        session_id: SessionIdRequired,
        auth_service: AuthServiceDep,
    ) -> UserSchema:
        user_auth: Authorization = await auth_service.get_authorization(session_id)
        if user_auth['user'].role < self.min_role:
            raise ForbiddenAccess(
                detail='You do not have permission to access this resource.',
                headers={
                    'WWW-Authenticate': f'Bearer scope="{self.min_role.name}"'
                }
            )

        if self.auto_extend_sessions:
            await auth_service.extend_authorization(user_auth)

        return user_auth['user']