from .schemas import AccessTokenPayload, EncodedToken, JWTPayload, RefreshTokenPayload, UserOAuthData
from enum import Enum
from .redis_client import RedisClient
import jwt
from api.config.settings import app_config
from typing import Optional
from api.utils.errors import HTTPUnauthorizedToken
from pydantic import ValidationError


class TokenTypes(str, Enum):
    ACCESS = 'access'
    REFRESH = 'refresh'


def encode_token(payload: JWTPayload) -> str:
    return jwt.encode(
        payload.model_dump(),
        app_config.JWT_SECRET_KEY,
        algorithm=app_config.JWT_ALGORITHM
    )


def decode_token(encoded_token: str, options: Optional[dict] = None) -> dict:
    return jwt.decode(
        encoded_token,
        app_config.JWT_SECRET_KEY,
        algorithms=[app_config.JWT_ALGORITHM],
        options=options
    )


class JWTService:
    @staticmethod
    async def create_token(username: str, user_role: str, token_type: TokenTypes) -> str:
        '''
        Encodes the username and user role into a JWT token

        Arguments:
            username {str} 
            user_role {str} 
            token_type {TokenTypes} - TokenTypes.ACCESS or TokenTypes.REFRESH

        Returns:
            The encoded token payload 
        '''
        payload_type = (
            AccessTokenPayload if token_type == TokenTypes.ACCESS
            else RefreshTokenPayload
        )

        token_payload = payload_type(
            sub=username,
            role=user_role,
        )

        encoded_token = encode_token(token_payload)
        return encoded_token

    @staticmethod
    async def decode_access_token(encoded_token: str) -> AccessTokenPayload:
        '''
        Decodes the encoded access token and returns the decoded payload.

        Arguments:
            encoded_token {str}

        Raises:
            When the token has expired, the tokens JTI is blacklisted and
            an HTTPUnauthorizedToken is raised.  

            When the token type is not 'access', an HTTPUnauthorizedToken is raised.

            If the payload format is invalid, a HTTPUnauthorizedToken is raised.
        Returns:
            AccessTokenPayload -- _description_
        '''
        decoded_token = None
        try:
            decoded_token = decode_token(encoded_token)
            token_type = decoded_token.get('type')
            if not token_type or token_type != TokenTypes.ACCESS:
                raise HTTPUnauthorizedToken()

            return AccessTokenPayload(
                **decoded_token
            )
        
        except jwt.ExpiredSignatureError:
            await JWTService.revoke_expired_token(encoded_token)
            raise HTTPUnauthorizedToken()
        
        except (ValueError, jwt.PyJWTError, ValidationError):
            raise HTTPUnauthorizedToken()
    
    
    @staticmethod
    async def get_refresh_token(encoded_token) -> RefreshTokenPayload:
        '''
        Decodes a passed 'refresh_token' encoding from the request cookie 
        and returns the decoded payload.

        Arguments:
            encoded_token {_type_} 

        Raises:
            HTTPUnauthorizedToken: when fails to decode or has expired

        Returns:
            RefreshTokenPayload 
        '''
        try:
            user_token_encoded = decode_token(encoded_token)
            return RefreshTokenPayload(
                **user_token_encoded
            )
        except (jwt.PyJWTError, ValidationError):
            raise HTTPUnauthorizedToken()

    @staticmethod
    async def revoke_expired_token(encoded_token: str) -> None:
        '''
        Revokes the token by decoding the token and blacklisting the token jti

        Arguments:
            encoded_token {str}
        '''
        try:
            decoded_token = decode_token(
                encoded_token, options={'verify_exp': False}
            )
            token_jti = decoded_token.get('jti')
            if token_jti:
                await RedisClient.blacklist_token(token_jti, encoded_token)
        except Exception:
            pass

    @staticmethod
    async def revoke(token_jti: str, token: str) -> None:
        '''
        Blacklists the token using the token_jti and token

        Arguments:
            token_jti {str} -- the token jti; (json token identifier)
            token {str} -- the token encoding 
        '''
        await RedisClient.blacklist_token(token_jti, token)

    @staticmethod
    async def has_revoked(token_jti: str) -> bool:
        '''
        Returns True if the token_jti is blacklisted in redis 
        Arguments:
            token_jti {str}
        '''
        return await RedisClient.has_blacklisted(token_jti)
