from typing import Annotated

from fastapi import Depends, Request

from api.exceptions.http import HTTPForbidden
from app.api.schemas.users import UserModel
from app.infrastructure.security.roles import Role

from ..auth.depends import SessionRequiredDep
from ..depends import DatabaseDep
from .service import UserService  # Import here to avoid circular dependency


async def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)


UserServiceDepends = Depends(get_user_service)
UserServiceDep = Annotated[UserService, UserServiceDepends]


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
    return await user_service.get_current_user(session.user_id)


CurrentUserDepends = Depends(get_current_user)
CurrentUserDep = Annotated[UserModel, CurrentUserDepends]


def role_required(min_role: Role):
    async def role_check(current_user: CurrentUserDep) -> UserModel:
        """Dependency to check if the current user has the required role."""
        if current_user.role < min_role:
            raise HTTPForbidden(
                'You do not have the required permissions to perform this action.'
            )
        return current_user

    return Depends(role_check)


ReadOnlyRequired = Depends(role_required(Role.READ_ONLY))
RoleDep = Annotated[UserModel, Depends(role_required(Role.READ_ONLY))]

AdminRequired = Depends(role_required(Role.ADMIN))
AdminRequiredDep = Annotated[UserModel, Depends(role_required(Role.ADMIN))]

UserRequired = Depends(role_required(Role.USER))
UserRequiredDep = Annotated[UserModel, Depends(role_required(Role.USER))]
