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
    async def create_token(username: str, user_role: str, token_type: TokenTypes) -> tuple[str, str]:

        payload_type = (
            AccessTokenPayload if token_type == TokenTypes.ACCESS
            else RefreshTokenPayload
        )

        token_payload = payload_type(
            sub=username,
            role=user_role,
        )
        
        encoded_token = encode_token(token_payload)
        return token_payload.jti, encoded_token

    @staticmethod
    async def decode_access_token(encoded_token: str) -> AccessTokenPayload:
        decoded_token = None
        try:
            decoded_token = decode_token(encoded_token)
            if not decoded_token.get('type') or decoded_token['type'] != TokenTypes.ACCESS:
                raise HTTPUnauthorizedToken()

            return AccessTokenPayload(
                **decoded_token
            )
        except jwt.ExpiredSignatureError:
            if decoded_token:
                await RedisClient.blacklist_token(
                    decoded_token['jti'], encoded_token
                )
            raise HTTPUnauthorizedToken()

        except (ValueError, jwt.PyJWTError, ValidationError):
            raise HTTPUnauthorizedToken()

    @staticmethod
    async def get_refresh_token(refresh_token) -> RefreshTokenPayload:
        try:
            user_token_encoded = decode_token(refresh_token)
            print(user_token_encoded)
            return RefreshTokenPayload(
                **user_token_encoded
            )
        except (jwt.PyJWTError, ValidationError) as e:
            print(f'Error: {e}')
            raise HTTPUnauthorizedToken()

    @staticmethod
    async def revoke(token_jti: str, token: str) -> None:
        await RedisClient.blacklist_token(token_jti, token)

    @staticmethod
    async def has_revoked(token_jti: str) -> None:
        await RedisClient.has_blacklisted(token_jti)
