from typing import Annotated
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
from api.models.user import UserRoles
from api.config.settings import app_config
from .schemas import (
    TokenPair,
    TokenType
)
import uuid


class InvalidTokenError(HTTPException):
    '''Raised when a token is invalid or expired'''

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Invalid or expired token, please try again'
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
oauth_login = Annotated[OAuth2PasswordRequestForm, Depends()]
token_required = Annotated[str, Depends(oauth2_scheme)]


class JWTManager:
    ACCESS_TOKEN_EXPR = timedelta(minutes=30)
    REFRESH_TOKEN_EXPR = timedelta(days=1)

    @staticmethod
    def create_token(user_data: dict, token_type: TokenType) -> str:
        '''
        Creates an encoded JWT token based on the user data and token type
        & assigns a expiration time based on the token type

        Arguments:
            user_data {dict} -- {sub: user.username, role: user.role}
            token_type {TokenType} -- TokenType.ACCESS or TokenType.REFRESH
        Returns:
            str -- the encoded JWT token
        '''
        token_expr = (
            JWTManager.ACCESS_TOKEN_EXPR if token_type == TokenType.ACCESS
            else JWTManager.REFRESH_TOKEN_EXPR
        )

        jwt_encoding = {
            'sub': user_data['sub'],
            'role': user_data['role'],
            'type': token_type,
            'exp': datetime.now(timezone.utc) + token_expr,
            'jti': str(uuid.uuid4())
        }

        return jwt.encode(
            jwt_encoding,
            app_config.JWT_SECRET_KEY,
            algorithm=app_config.JWT_ALGORITHM
        )

    @staticmethod
    def create_token_pair(user_data: dict) -> TokenPair:
        '''
        Creates a pair of JWT tokens (access and refresh tokens) based on the user 
        data with the 'bearer' set by default in TokenPair pydantic model

        Arguments:
            user_data {dict} -- {sub: user.username, role: user.role}
        Returns:
            TokenPair
        '''
        return TokenPair(
            access_token=JWTManager.create_token(
                user_data,
                TokenType.ACCESS
            ),
            refresh_token=JWTManager.create_token(
                user_data,
                TokenType.REFRESH
            )
        )

    @staticmethod
    def resolve_token(token_str: str) -> dict:
        '''
        Decodes a JWT token and returns the payload

        Arguments:
            token_str {str} -- the encoded JWT token

        Returns:
            dict -- the decoded JWT token payload
        '''
        payload = jwt.decode(
            token_str,
            app_config.JWT_SECRET_KEY,
            algorithms=[app_config.JWT_ALGORITHM]
        )

        if JWTManager.token_is_blacklisted(payload['jti']):
            raise InvalidTokenError()

        payload['role'] = UserRoles(payload['role'])
        return payload

    @staticmethod
    def try_decode_token(token: str) -> dict:
        '''
        Attempts to decode a JWT token and returns the payload if successful
        of the user data and token type

        Arguments:
            token {str} -- _description_

        Raises:
            HTTPException: 403 Forbidden if the token is invalid or expired
        Returns:
            dict -- the decoded JWT token payload
        '''
        try:
            return JWTManager.resolve_token(token)

        except jwt.ExpiredSignatureError:
            JWTManager.blacklist_token(token)
            raise InvalidTokenError()

        except jwt.PyJWTError:
            raise InvalidTokenError()

    @staticmethod
    def blacklist_token(token: str) -> None:
        # TODO
        pass

    @staticmethod
    def token_is_blacklisted(token: str) -> bool:
        # TODO
        return False

    @staticmethod
    def try_refresh_access(refresh_token: str) -> TokenPair:
        payload = JWTManager.try_decode_token(refresh_token)
        if payload["type"] != TokenType.REFRESH:
            raise InvalidTokenError()
        user_data = {
            "sub": payload["sub"],
            "role": payload["role"]
        }
        JWTManager.blacklist_token(refresh_token)
        return JWTManager.create_token_pair(user_data)
