from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends


from app.core.db import get_db
from app.core.security.models import ClientIdentity
from app.models.user import User, Role
from app.core.security import (
    get_current_user,
    RoleRequired,
    get_client_identity,
    SessionAuth
)

requires_db = Annotated[AsyncSession, Depends(get_db)]
current_user = Annotated[User, Depends(get_current_user)]
client_identity = Annotated[ClientIdentity, Depends(get_client_identity)]

class UserRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.USER)


class AdminRequired(RoleRequired):
    def __init__(self) -> None:
        super().__init__(Role.ADMIN)

role_required = Annotated[User, Depends(RoleRequired())]
user_required = Annotated[User, Depends(UserRequired())]
admin_required = Annotated[User, Depends(AdminRequired())]
