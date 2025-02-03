from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.db import get_db
from app.models.user import User, UserRole


from .auth import (
    get_current_user,
    require_role,
    auth_schema,
    session_identity
)


requires_db = Annotated[AsyncSession, Depends(get_db)]

CurrentUser = Annotated[User, Depends(get_current_user)]

user_protected = Annotated[User, Depends(require_role(UserRole.USER))]
admin_protected = Annotated[User, Depends(require_role(UserRole.ADMIN))]






















