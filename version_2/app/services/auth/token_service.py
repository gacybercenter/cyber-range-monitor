from jose import JWTError, jwt
from typing import Optional
from pydantic import ValidationError

from app.core import settings
from app.schemas.auth_schemas import (
    AccessTokenPayload,
    EncodedToken,
    JWTPayload,
    UserOAuthData
)
from app.common.errors import HTTPUnauthorizedToken


class TokenService:
    def _encode(self, payload: AccessTokenPayload) -> str:
        return jwt.encode(
            payload.model_dump(),
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )

    def decode_token(self, encoded_token: str, options: Optional[dict] = None) -> dict:
        return jwt.decode(
            encoded_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options=options
        )

    def create_access_token(self, oauth_data: UserOAuthData) -> EncodedToken:
        access_token = self._encode(
            AccessTokenPayload(
                sub=oauth_data.sub,
                role=oauth_data.role
            )
        )
        return EncodedToken(access_token=access_token)

    def try_decode(self, encoded_token: str) -> AccessTokenPayload:
        try:
            return AccessTokenPayload(
                **self.decode_token(encoded_token)
            )
        except Exception:
            raise HTTPUnauthorizedToken()
        
        

def get_token_service() -> TokenService:
    return TokenService()

