from re import A
from typing import Annotated, Any, Callable, Coroutine
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


from app.api.errors import HTTPForbidden, HTTPNotFound
from app.common.errors import HTTPUnauthorized
from app.core.db import get_db
from app.core.security import SessionAuthSchema
from app.core.security.auth_schema import get_session_schema
from app.core.security.models import InboundSession
from app.models.user import User, UserRole
from app.schemas.session_schema import SessionData
from app.services import auth_service
from app.services.auth_service import AuthService


auth_schema = Annotated[SessionData, Depends(SessionAuthSchema)]
session_identity = Annotated[InboundSession, Depends(get_session_schema)]

async def get_current_user(
    session_auth: auth_schema,
    db: AsyncSession = Depends(get_db)
) -> User:
    '''_summary_
    Gets the current user from the associated session from the Users table

    Keyword Arguments:
        session_data {SessionData} --  {Depends(SessionAuthSchema())})
        db {AsyncSession} -- _description_ (default: {Depends(get_db)})

    Raises:
        HTTPException: 404 if the user is not found

    Returns:
        User
    '''
    auth = AuthService()
    existing_user = await auth.get_username(session_auth.username, db)
    if not existing_user:
        raise HTTPNotFound('User')

    mapped_user = session_auth.client_identity.model_dump().get('mapped_user')

    if mapped_user != 'Unknown' and mapped_user != existing_user.username:
        raise HTTPUnauthorized(
            'Untrusted session identity'
        )

    return existing_user


def require_role(min_role: UserRole) -> Callable[[User], Coroutine[Any, Any, User]]:
    '''_summary_
    Checks if the user has the role required to access the resource
    
    Arguments:
        min_role {UserRole}

    Returns:
        Callable[[User], Coroutine[Any, Any, User]]
    '''
    async def role_checker(
      user: User = Depends(get_current_user)  
    ) -> User:
        if user.role < min_role:
            raise HTTPForbidden('You lack the required permissions to access this resource')
        return user
    
    return role_checker
    
    
    





