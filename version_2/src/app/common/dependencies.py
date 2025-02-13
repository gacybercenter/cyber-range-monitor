from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


from app.db import get_db
from app.security.models import ClientIdentity
from app.models.user import User, Role
from app.security import (
    get_current_user,
    RoleRequired,
    get_client_identity,
    SessionAuth
)

DatabaseRequired = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
IdentityRequired = Annotated[ClientIdentity, Depends(get_client_identity)]

class UserRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.USER)


class AdminRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.ADMIN)

RoleProtected = Annotated[User, Depends(RoleRequired())]
UserProtected = Annotated[User, Depends(UserRequired())]
AdminProtected = Annotated[User, Depends(AdminRequired())]
