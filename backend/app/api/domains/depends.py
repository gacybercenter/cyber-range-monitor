from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, Request, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure import db, redis
from app.infrastructure.security.roles import Role
from app.infrastructure.security.sessions import SessionId

from ..exceptions.http import HTTPForbidden
from ..schemas.auth import SessionPayload
from ..schemas.users import UserModel
from .auth import SessionSecurity, SessionService
from .health_services import DatabaseHealthService, RedisHealthService
from .users import UserService

DatabaseDepends = Depends(db.get_session)
DatabaseDep = Annotated[AsyncSession, DatabaseDepends]

RedisDepends = Depends(redis.get_redis_client)
RedisDep = Annotated[aioredis.Redis, RedisDepends]


async def get_db_health_service(db: DatabaseDep) -> DatabaseHealthService:
    """Dependency to get the database health service."""
    return DatabaseHealthService(db=db)


async def get_redis_health_service(redis: RedisDep) -> RedisHealthService:
    return RedisHealthService(redis_client=redis)


RedisHealthDep = Annotated[RedisHealthService, Depends(get_redis_health_service)]
DatabaseHealthDep = Annotated[DatabaseHealthService, Depends(get_db_health_service)]

SessionIdSecurity = SessionSecurity()
SessionIdRequired = Security(SessionIdSecurity)
SessionIdDep = Annotated[SessionId, SessionIdRequired]


async def get_session_service(redis: RedisDep) -> SessionService:
    return SessionService(redis)


SessionServiceDepends = Depends(get_session_service)
SessionServiceDep = Annotated[SessionService, SessionServiceDepends]


async def get_session_payload(
    request: Request,
    session_id: SessionIdDep,
    session_service: SessionServiceDep,
) -> SessionPayload:
    """
    Dependency to ensure that a session ID is present in the request.
    If not, it returns None, allowing the caller to handle the absence of a session ID.
    """
    fingerprint = request.state.fingerprint
    return await session_service.load_session(
        id=session_id,
        inbound_client=fingerprint,
    )


SessionRequiredDepends = Depends(get_session_payload)
SessionRequiredDep = Annotated[SessionPayload, SessionRequiredDepends]


async def get_user_service(db: DatabaseDep) -> UserService:
    return UserService(db)


UserServiceDepends = Depends(get_user_service)
UserServiceDep = Annotated[UserService, UserServiceDepends]


async def get_current_user(
    request: Request, session: SessionRequiredDep, user_service: UserServiceDep
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
AdminRequiredDep = Annotated[UserModel, AdminRequired]

UserRequired = Depends(role_required(Role.USER))
UserRequiredDep = Annotated[UserModel, UserRequired]
