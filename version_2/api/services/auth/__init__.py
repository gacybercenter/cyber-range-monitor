from typing import Annotated, Callable, Coroutine, Any
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer


from api.models.user import UserRoles
from .jwt_service import JWTService, TokenTypes
from api.schemas.auth_schemas import (
    UserOAuthData,
    EncodedToken,
    JWTPayload,
    RefreshTokenPayload,
    AccessTokenPayload
)
from api.core.errors import HTTPUnauthorizedToken, HTTPForbidden


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
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
    payload = await JWTService.decode_access_token(token)
    if payload.type != TokenTypes.ACCESS:
        raise HTTPUnauthorizedToken()

    return UserOAuthData(
        sub=payload.sub,
        role=payload.role
    )


def role_level_allowed(minimum_role: UserRoles) -> Callable[
    [UserOAuthData], Coroutine[Any, Any, UserOAuthData]
]:
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
        if not UserRoles(current_user.role) >= minimum_role:
            raise HTTPForbidden(
                'You do not have the required permissions to access this resource'
            )

        return current_user

    return role_checker


require_auth = role_level_allowed(UserRoles.read_only)
user_required = role_level_allowed(UserRoles.user)
admin_required = role_level_allowed(UserRoles.admin)
