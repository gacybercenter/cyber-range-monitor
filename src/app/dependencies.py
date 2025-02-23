from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from app.db import get_db
from app.sessions.constant import SESSION_AUTHORITY
from app.sessions.schemas import SessionData
from app.users.models import User
from app.extensions.auth import (
    get_current_user,
    RoleProtected,
    AdminProtected,
    UserProtected,
)

DatabaseRequired = Annotated[AsyncSession, Depends(get_db)]
AuthRequired = Annotated[SessionData, Depends(SESSION_AUTHORITY)]
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminRequired = Annotated[User, Depends(AdminProtected())]
UserRequired = Annotated[User, Depends(UserProtected())]
RoleRequired = Annotated[User, Depends(RoleProtected())]
