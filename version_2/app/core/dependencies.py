from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.db import get_db
from app.services.auth.core import oauth2_scheme, get_current_user, role_level_allowed
from app.models.user import UserRoles
from app.schemas.auth_schemas import UserOAuthData


token_required = Annotated[str, Depends(oauth2_scheme)]
needs_db = Annotated[AsyncSession, Depends(get_db)]
current_user = Annotated[UserOAuthData, Depends(get_current_user)]

require_auth = role_level_allowed(UserRoles.read_only)
user_required = role_level_allowed(UserRoles.user)
admin_required = role_level_allowed(UserRoles.admin)


