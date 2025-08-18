from typing import Annotated

from fastapi import Depends, Request, Security

from app.infrastructure.depends import db_depends_factory, redis_depends_factory
from app.infrastructure.security.roles import Role

from ..exceptions.http import HTTPForbidden
from ..schemas.auth import SessionInfo
from ..schemas.users import UserModel
from .auth.scheme import SessionIDBearer
from .auth.service import SessionService
from .users.service import UserService

SessionIdRequired = Annotated[str | None, Security(SessionIDBearer)]
get_session_service = redis_depends_factory(SessionService)
SessionServiceDep = Annotated[
    SessionService,
    Depends(get_session_service),
]


async def session_required(
    request: Request,
    session_id: SessionIdRequired,
    session_service: SessionServiceDep,
) -> SessionInfo:
    """
    Dependency to ensure that a session ID is present in the request.
    If not, it returns None, allowing the caller to handle the absence of a session ID

    Raises
    ------

    HTTPUnauthorized -- Session ID Bearer is not
    HTTPForbidden -- Invalid or expired session ID
    """
    fingerprint = request.state.fingerprint
    session = await session_service.get_session(
        unsigned_id=session_id,
        client=fingerprint
    )
    request.state.session = session
    return session


SessionRequiredDep = Annotated[SessionInfo, Depends(session_required)]

get_user_service = db_depends_factory(UserService)
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_current_user(
    request: Request,
    session: SessionRequiredDep,
    user_service: UserServiceDep
) -> UserModel:
    """
    Dependency to get the current user service.
    This can be used in routes to access user-related operations.
    """
    if request.state.user:
        return request.state.user
    current_user = await user_service.get_current_user(session.user_id)
    request.state.user = current_user
    return current_user

CurrentUserDep = Annotated[UserModel, Depends(get_current_user)]


def role_required(min_role: Role):
    async def role_check(current_user: CurrentUserDep) -> UserModel:
        """Dependency to check if the current user has the required role."""
        if current_user.role < min_role:
            raise HTTPForbidden(
                'You do not have the required permissions to perform this action.'
            )
        return current_user

    return role_check


ReadOnlyRequired = role_required(Role.READ_ONLY)
RoleDep = Annotated[UserModel, Depends(ReadOnlyRequired)]

AdminRequired = role_required(Role.ADMIN)
AdminRequiredDep = Annotated[UserModel, Depends(AdminRequired)]

UserRequired = role_required(Role.USER)
UserRequiredDep = Annotated[UserModel, Depends(UserRequired)]
