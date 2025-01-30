from annotated_types import T
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRoles
from typing import Optional

from app.schemas.auth_schemas import UserOAuthData, TokenTypes


from app.services.auth.token_service import TokenService
from app.services.redis_service import RedisClient
from app.services.mixins import CRUDService
from app.common.errors import HTTPNotFound, HTTPUnauthorizedToken
from app.core.security import hashing
from app.schemas.auth_schemas import SessionData


class AuthService:
    def __init__(self) -> None:
        self._controller = CRUDService(User)
        self.token_manager = TokenService()

    async def authenticate_user(
        self,
        form_username: str,
        form_password: str,
        db: AsyncSession
    ) -> Optional[User]:
        user = await self._controller.get_by(User.username == form_username, db)
        if user is None:
            return None

        if not hashing.check_pwd(form_password, user.password_hash):  # type: ignore
            return None

        return user

    async def create_session(self, oauth_data: UserOAuthData) -> SessionData:
        redis = RedisClient.get_instance()
        payload = self.token_manager.create_access_token(oauth_data)

        session_id = await redis.create_session(oauth_data.sub)
        await redis.set_access_token(
            oauth_data.sub,
            payload.access_token
        )
        return SessionData(
            access_token=payload.access_token,
            session_id=session_id
        )

    async def refresh_session(self, session_id: str, db: AsyncSession) -> SessionData:
        existing_user = await self.session_to_user(session_id, db)
        redis = RedisClient.get_instance()
        await redis.delete_access_token(existing_user.username)  # type: ignore
        oauth_data = UserOAuthData(
            sub=existing_user.username,  # type: ignore
            role=existing_user.role  # type: ignore
        )

        token_encoding = self.token_manager.create_access_token(oauth_data)
        await redis.set_access_token(
            oauth_data.sub,
            token_encoding.access_token
        )
        return SessionData(
            access_token=token_encoding.access_token,
            session_id=session_id
        )

    async def end_session(self, session_id: str, db: AsyncSession) -> None:
        existing_user = await self.session_to_user(session_id, db)
        redis = RedisClient.get_instance()
        await redis.delete_access_token(existing_user.username)  # type: ignore
        await redis.delete_session(session_id)

    async def session_to_user(self, session_id: str, db: AsyncSession) -> Optional[User]:
        redis = RedisClient.get_instance()
        username = await redis.get_session(session_id)
        if not username:
            raise HTTPUnauthorizedToken()

        await redis.delete_access_token(username)

        existing_user = await self._controller.get_by(
            User.username == username,
            db
        )
        if existing_user is None:
            raise HTTPNotFound('User')

        return existing_user


def get_auth_service() -> AuthService:
    return AuthService()
