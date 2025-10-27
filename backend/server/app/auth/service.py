from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

from server.app.auth import utils as auth_utils
from server.app.auth.errors import (
    InvalidTokenError,
    RoleForbiddenError,
)
from server.app.auth.repo import TokenKey, TokenStore
from server.app.auth.schema import (
    AccessToken,
    RefreshToken,
    SessionData,
    SessionList,
    TokenClaim,
)

if TYPE_CHECKING:

    from fastapi import Response

    from server.app.users.schema import InternalUser
    from server.enums import UserRoles
    from server.headers import ClientInfo

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AuthenticationService:
    tokens: TokenStore

    async def authorize(
        self,
        user: InternalUser,
        client: ClientInfo,
        response: Response,
    ) -> TokenClaim:
        '''
        Creates access and refresh tokens for a user and stores
        the refresh claim in Redis.

        Parameters
        ----------
        user : InternalUser
            The user to authorize.
        client : ClientInfo
            The client information (IP, user-agent).
        response : Response
            The HTTP response to set cookies on.

        Returns
        -------
        TokenClaim
        '''
        session_id = str(uuid.uuid4())
        access, refresh = auth_utils.create_token_pair(user, session_id)
        session_data = SessionData(
            ip_address=client.ip_address,
            user_agent=client.user_agent,
            created_at=refresh.issued_at,
            user_id=str(user.id),
            username=user.username,
            last_used_at=refresh.issued_at,
            session_id=session_id,
        )

        await self.tokens.save_token(
            TokenKey('access', session_id, str(user.id)),
            exp=access.exp,
            metadata=session_data.to_hashable()
        )

        await self.tokens.save_token(
            TokenKey('refresh', session_id, str(user.id)),
            exp=refresh.exp,
            metadata=session_data.to_hashable()
        )

        await self.tokens.set_cver(user_id=str(user.id), cver=user.cver)

        auth_utils.set_refresh_token_cookie(response, refresh.encoded)

        return TokenClaim(
            access_token=access.encoded,
            refresh_token=refresh.encoded,
            token_type='bearer',
            max_age=refresh.expires,
            expires=refresh.exp,
        )

    async def verify_access_token(self, token: str) -> AccessToken:
        """
        Decode with server-side checks such as blacklisting and
        credential version verification to prevent stale or revoked tokens.

        Parameters
        ----------
        token : str
            The JWT token string to decode.
        expected_type : str
            The expected token type ('access' or 'refresh').

        Returns
        -------
        JwtClaim

        Raises
        ------
        InvalidTokenError
            If the token is revoked, invalid or stale.
        """
        claim = auth_utils.load_jwt_claim(token, expected_type='access')
        try:
            token_data = AccessToken.convert(claim)
        except Exception:
            raise InvalidTokenError('token_invalid_format')

        await auth_utils.verify_token_state(token_data, self.tokens)

        return token_data

    async def verify_refresh_token(self, token: str) -> RefreshToken:
        claim = auth_utils.load_jwt_claim(token, expected_type='refresh')
        try:
            token_data = RefreshToken.convert(claim)
        except Exception:
            raise InvalidTokenError('token_invalid_format')

        await auth_utils.verify_token_state(token_data, self.tokens)

        return token_data

    async def refresh_session(
        self,
        old_refresh: RefreshToken,
        client: ClientInfo,
        response: Response,
        user: InternalUser,
    ) -> TokenClaim:
        await self.tokens.delete_session_tokens(
            session_id=old_refresh.sid,
            user_id=old_refresh.sub,
        )
        auth_utils.delete_refresh_token_cookie(response)
        return await self.authorize(user, client, response)

    async def require_role(self, min_role: UserRoles, access: AccessToken) -> AccessToken:
        if access.scope < min_role:
            raise RoleForbiddenError(access.scope)
        return access

    async def list_sessions(
        self,
        user_id: str,
        current_session_id: str | None
    ) -> SessionList:
        sessions = await self.tokens.list_session_data(user_id)
        return SessionList(
            sessions=[
                SessionData.convert(session)
                for session in sessions
            ],
            current_session_id=current_session_id,
        )
