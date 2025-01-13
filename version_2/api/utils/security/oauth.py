from typing import Annotated, Optional, Union
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from api.models.user import UserRoles
from api.config.settings import app_config
from enum import Enum
from typing import Callable



class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserOAuthPayload(BaseModel):
    sub: str
    role: str
    type: TokenType


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
oauth_login = Annotated[OAuth2PasswordRequestForm, Depends()]

ACCESS_TOKEN_EXPR = timedelta(minutes=30)
REFRESH_TOKEN_EXPR = timedelta(days=1)


def create_token(
    user_data: dict,
    token_type: TokenType
) -> str:
    token_expr = (
        ACCESS_TOKEN_EXPR if token_type == TokenType.ACCESS 
        else REFRESH_TOKEN_EXPR
    )
    
    jwt_encoding = {
        'sub': user_data['sub'],
        'role': user_data['role'],
        'type': token_type,
        'exp': datetime.now(timezone.utc) + token_expr
    }
    
    return jwt.encode(
        jwt_encoding,
        app_config.JWT_SECRET_KEY,
        algorithm=app_config.JWT_ALGORITHM
    )


def create_tokens(user_data: dict) -> Token:
    return Token(
        access_token=create_token(
            user_data,
            TokenType.ACCESS
        ),
        refresh_token=create_token(
            user_data,
            TokenType.REFRESH
        )
    )

def blacklist_token(token: str) -> None:
    # Implement token blacklisting
    pass



async def try_decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            app_config.JWT_SECRET_KEY,
            algorithms=[app_config.JWT_ALGORITHM]
        )
        payload['role'] = UserRoles(payload['role'])
        return payload
    except jwt.ExpiredSignatureError:
        blacklist_token(token)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid or expired token'
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid or expired token'
        )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> dict:
    payload = await try_decode_token(token)
    if payload['type'] != TokenType.ACCESS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid token type'
        )
    return {
        'sub': payload['sub'],
        'role': payload['role']
    }
    

async def refresh_access_token(refresh_token: str) -> Token:
    payload = await try_decode_token(refresh_token)
    if payload["type"] != TokenType.REFRESH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token type"
        )
    user_data = {
        "sub": payload["sub"],
        "role": payload["role"]
    }
    return create_tokens(user_data)
