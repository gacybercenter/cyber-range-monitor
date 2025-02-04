from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


from app.core.db import get_db
from app.models.user import User, Role
from app.core.security import (
    get_current_user,
    RoleRequired,
    get_session_schema
)


requires_db = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


class UserRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.USER)


class AdminRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.ADMIN)



session_identity= Annotated[User, Depends(get_session_schema)] 

role_required = Annotated[User, Depends(RoleRequired())]
user_required = Annotated[User, Depends(UserRequired())]
admin_required = Annotated[User, Depends(AdminRequired())]
