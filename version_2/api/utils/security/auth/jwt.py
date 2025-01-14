# jwt.py
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import datetime, timedelta, timezone
import uuid
import redis
from typing import Optional

from api.utils.errors import InvalidTokenError
from api.models.user import UserRoles
from api.config.settings import app_config
from .schemas import (
    TokenPair,
    TokenType,
    UserOAuthData
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
token_required = Annotated[str, Depends(oauth2_scheme)]


def decode_token(token_encoding: str, options: Optional[dict] = None) -> dict:
    '''
    Returns the decoded JWT token payload with proper configurations 

    Arguments:
        token_encoding {str} -- the encoded JWT token

    Keyword Arguments:
        options {Optional[dict]} -- optional configurations for decoding the token (default: {None})

    Returns:
        the decoded JWT token payload

    Raises:
        py.jwt.PyJWTError: if the token is invalid or expired, call with try-exc 
    '''
    return jwt.decode(
        token_encoding,
        app_config.JWT_SECRET_KEY,
        algorithms=[app_config.JWT_ALGORITHM],
        options=options
    )


def create_token(user_data: UserOAuthData, token_type: TokenType) -> str:
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

    now = datetime.now(timezone.utc) + token_expr

    # change as needed
    jwt_encoding = {
        'sub': user_data.sub,
        'role': user_data.role,
        'type': token_type,
        'exp': now + token_expr,
        'iat': now,
        'jti': str(uuid.uuid4()),
    }

    return jwt.encode(
        jwt_encoding,
        app_config.JWT_SECRET_KEY,
        algorithm=app_config.JWT_ALGORITHM
    )


class JWTManager:
    ACCESS_TOKEN_EXPR = timedelta(minutes=30)
    REFRESH_TOKEN_EXPR = timedelta(days=1)

    _redis_client = redis.Redis(
        host=app_config.REDIS_HOST,
        port=app_config.REDIS_PORT,
        db=app_config.REDIS_DB,
        decode_responses=True
    )

    @staticmethod
    def init_token_pair(user_data: UserOAuthData) -> TokenPair:
        '''
        Creates a pair of JWT tokens (access and refresh tokens) based on the user 
        data with the 'bearer' set by default in TokenPair pydantic model

        Arguments:
            user_data {dict} -- {sub: user.username, role: user.role}
        Returns:
            TokenPair
        '''
        return TokenPair(
            access_token=create_token(user_data, TokenType.ACCESS),
            refresh_token=create_token(user_data, TokenType.REFRESH)
        )

    @staticmethod
    def resolve_token(token_encoding: str) -> dict:
        '''
        Decodes a JWT token and returns the payload

        Arguments:
            token_encoding {str} -- the encoded JWT token
        Returns:
            dict -- the decoded JWT token payload
        Raises:
            InvalidTokenError: if the token is blacklist or invalid 
            jwt.PyJWTError: (implicit)    
        '''
        payload = decode_token(token_encoding)
        token_jti = payload.get('jti')
        if not token_jti or JWTManager.is_token_blacklisted(token_jti):
            raise InvalidTokenError()

        payload['role'] = UserRoles(payload['role'])
        return payload

    @staticmethod
    def try_decode_token(token_encoding: str) -> dict:
        '''
        Attempts to decode a JWT token and returns the payload if successful
        of the user data and token type, safely handles decoding errors with 
        appropriate responses

        Arguments:
            token {str} -- _description_

        Raises:
            InavlidTokenError: if the token format is invalid, expired or jti blacklisted
        Returns:
            dict -- the decoded JWT token payload
        '''
        try:

            return JWTManager.resolve_token(token_encoding)

        except jwt.ExpiredSignatureError:
            # blacklist expired tokens
            JWTManager.blacklist_token(token_encoding)
            raise InvalidTokenError()

        except (jwt.PyJWTError, ValueError):
            raise InvalidTokenError()

    @staticmethod
    def try_refresh_access(refresh_token: str) -> TokenPair:
        payload = JWTManager.try_decode_token(refresh_token)
        if payload["type"] != TokenType.REFRESH:
            raise InvalidTokenError()

        try:
            user_data = UserOAuthData(
                sub=payload['sub'],
                role=payload['role']
            )
        except ValueError:
            raise InvalidTokenError()

        JWTManager.blacklist_token(refresh_token)
        return JWTManager.init_token_pair(user_data)

    @staticmethod
    def blacklist_token(token: str) -> None:
        try:
            payload = decode_token(token, options={'verify_exp': False})

            token_jti = payload.get('jti')
            if not token_jti:
                return

            exp = payload.get('exp')
            now = datetime.now(timezone.utc).timestamp()
            token_ttl = int(exp) - now
            if token_ttl <= 0:
                token_ttl = 1

            key = f"blacklist:{token_jti}"
            JWTManager._redis_client.setex(key, token_ttl, 'true')
        except Exception:
            pass

    @staticmethod
    def is_token_blacklisted(token_jti: str) -> bool:
        key = f"blacklist:{token_jti}"
        return JWTManager._redis_client.exists(key) == 1
