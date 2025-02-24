# 'Role Based Authentication / Authorization Control'
from typing import Annotated
from fastapi import Depends
from app.auth.service import SessionService, get_session_service
from .schemas import SessionData
from .constant import SESSION_AUTHORITY


SessionManager = Annotated[SessionService, Depends(get_session_service)]
AuthRequired = Annotated[SessionData, Depends(SESSION_AUTHORITY)]
