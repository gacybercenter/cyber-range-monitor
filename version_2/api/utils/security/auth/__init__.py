# auth package __init__.py
from typing import Annotated, Callable
from fastapi import Depends, HTTPException, status

from api.models.user import UserRoles
from api.utils.errors import AuthorizationRequired
from .jwt import (
    JWTManager, 
    token_required, 
    oauth_login, 
    oauth2_scheme
)
from .schemas import TokenType, TokenPair, UserOAuthData
from api.utils.errors import InvalidTokenError

async def get_current_user(token: token_required) -> UserOAuthData:
    payload = JWTManager.try_decode_token(token)
    if payload['type'] != TokenType.ACCESS:
        raise InvalidTokenError()
    
    return UserOAuthData(
        sub=payload['sub'],
        role=payload['role']
    )


def role_level_allowed(minimum_role: UserRoles) -> Callable:
    '''
    Specifies the minimum role level required to access a resource
    read_only = 1
    user = 2
    admin = 3

    Arguments:
        minimum_role {UserRoles} -- the minimum role level required to 
        access the resource
    Returns:
        Callable -- a dependency function that checks the current user's role
    '''
    async def role_checker(
        current_user: Annotated[dict, Depends(get_current_user)]
    ) -> dict:
        if not current_user["role"] >= minimum_role:
            raise AuthorizationRequired()
        
        return current_user

    return role_checker


auth_required = Annotated[dict, Depends(
    role_level_allowed(UserRoles.read_only))
]
user_required = Annotated[dict, Depends(
    role_level_allowed(UserRoles.user))
]
admin_required = Annotated[dict, Depends(
    role_level_allowed(UserRoles.admin)
)]
