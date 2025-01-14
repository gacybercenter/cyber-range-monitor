# auth package __init__.py
from typing import Annotated, Callable
from fastapi import Depends, HTTPException, status

from api.models.user import UserRoles
from api.utils.errors import AuthorizationRequired
from fastapi.security import OAuth2PasswordBearer
from .jwt import JWTManager
from .schemas import TokenType, TokenPair, UserOAuthData
from api.utils.errors import InvalidTokenError
from typing import Coroutine, Any

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
token_required = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(token: token_required) -> UserOAuthData:
    '''
    Returns the decoded UserOAuthData from the JWT token
    containing the 'sub' for the username and 'role' for the user's 
    role for the users permission level 

    Arguments:
        token {token_required} -- dependency requiring a valid JWT token
        for the current user 

    Raises:
        InvalidTokenError: _description_

    Returns:
        UserOAuthData -- _description_
    '''
    payload = JWTManager.try_decode_token(token)
    if payload['type'] != TokenType.ACCESS:
        raise InvalidTokenError()

    return UserOAuthData(
        sub=payload['sub'],
        role=payload['role']
    )


def role_level_allowed(
    minimum_role: UserRoles
) -> Callable[[UserOAuthData], Coroutine[Any, Any, UserOAuthData]]:
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
        current_user: Annotated[UserOAuthData, Depends(get_current_user)]
    ) -> UserOAuthData:
        if not current_user.role >= minimum_role:
            raise AuthorizationRequired()
        return current_user

    return role_checker


auth_required = Annotated[dict, Depends(oauth2_scheme)]
authorized_user = Annotated[dict, Depends(
    role_level_allowed(UserRoles.read_only))
]
user_required = Annotated[dict, Depends(
    role_level_allowed(UserRoles.user))
]
admin_required = Annotated[dict, Depends(
    role_level_allowed(UserRoles.admin)
)]
