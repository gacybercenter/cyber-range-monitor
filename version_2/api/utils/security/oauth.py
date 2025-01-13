from typing import Annotated, Optional
from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

from api.config.settings import app_config
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
oauth_login = Annotated[OAuth2PasswordRequestForm, Depends()]
# require_user = Annotated[str, Depends(get_current_user)]

ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE_MINUTES = timedelta(days=1)


class UserOAuthPayload(BaseModel):
    sub: str
    permission: str


def create_access_token(
    user_data: UserOAuthPayload,
    expires_delta: timedelta = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    jwt_encoding = user_data.model_dump()
    expires = datetime.now(timezone.utc) + expires_delta
    jwt_encoding.update({'exp': expires})
    return jwt.encode(
        jwt_encoding,
        app_config.JWT_SECRET_KEY,
        algorithm=app_config.JWT_ALGORITHM
    )


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(
            token,
            app_config.JWT_SECRET_KEY,
            algorithms=[app_config.JWT_ALGORITHM]
        )
        return {
            'sub': payload.get('sub'),
            'permission': payload.get('permission')
        }
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid or expired token'
        )
