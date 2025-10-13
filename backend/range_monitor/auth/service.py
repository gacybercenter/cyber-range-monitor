import contextlib
import logging
import uuid
from datetime import datetime

from fastapi.security import HTTPBearer
from jose import ExpiredSignatureError, JWTError
from starlette.requests import Request

from range_monitor.auth import tokens
from range_monitor.auth.errors import (
    AuthMissing,
    DoubleRotationConflict,
    InvalidJwtToken,
    RoleForbidden,
)
from range_monitor.auth.repo import SessionRepository
from range_monitor.auth.schema import JwtClaim, RefreshRequest, TokenClaim
from range_monitor.core.enums import UserRoles
from range_monitor.infra.security._policy import JwtPolicy

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def jwt_error_codes():
    """
    Context manager to translate JWT errors / decoding
    errors into application-specific exceptions.
    See `tokens.resolve_claim` for more details.

    Raises
    ------
    InvalidJwtToken
    """
    try:
        yield
    except ExpiredSignatureError:
        raise InvalidJwtToken('token_expired')
    except (JWTError, ValueError):
        raise InvalidJwtToken('token_invalid')
    except TypeError:
        raise InvalidJwtToken('invalid_token_type')


class AuthenticationService:
    def __init__(self, sessions: SessionRepository, jwt_policy: JwtPolicy) -> None:
        self.sessions = sessions
        self.jwt_policy = jwt_policy

    async def authorize(
        self, *, user_id: uuid.UUID, cver: int, role: UserRoles
    ) -> TokenClaim:
        """
        Creates access and refresh tokens for a user and stores
        the refresh claim in Redis.

        Parameters
        ----------
        user_id : uuid.UUID
        cver : int
        role : UserRoles

        Returns
        -------
        TokenClaim
        """
        sub = str(user_id)
        access_token, _ = tokens.create_claim(
            self.jwt_policy, 'access', user_id=sub, cver=cver, role=role
        )
        refresh_token, refresh_claim = tokens.create_claim(
            self.jwt_policy, 'refresh', user_id=sub, cver=cver, role=role
        )
        logger.info(f'saving claim for {user_id=} {refresh_claim.jti} w/ cver {cver}')
        await self.sessions.save_claim(
            jti=refresh_claim.jti,
            user_id=str(user_id),
            cver=cver,
            ttl=refresh_claim.time_to_live,
        )

        return TokenClaim(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            expires_at=datetime.fromtimestamp(refresh_claim.exp),
            issued_at=refresh_claim.iat,
        )

    def get_token_claim(self, token: str | None, expected_type: str) -> JwtClaim:
        if not token:
            raise AuthMissing()

        with jwt_error_codes():
            payload = tokens.decode_jwt_token(self.jwt_policy, token)
            claim = tokens.resolve_claim(payload, expected_type=expected_type)

        return claim

    async def decode_strict(self, token: str, expected_type: str) -> JwtClaim:
        claim = self.get_token_claim(token, expected_type)
        if await self.sessions.is_blacklisted(claim.jti):
            raise InvalidJwtToken('token_revoked')

        cached_cver = await self.sessions.get_cver(claim.sub)

        if cached_cver is None or cached_cver != claim.cver:
            logger.info(
                f'cver mismatch {cached_cver} {claim.cver} for {claim.sub} {claim.jti}'
            )
            await self.sessions.blacklist(claim.jti, claim.time_to_live)
            raise InvalidJwtToken('stale_token')

        return claim

    async def revoke_tokens(self, access_claim: JwtClaim, refresh_token: str) -> None:
        refresh_claim = self.get_token_claim(refresh_token, expected_type='refresh')

        if access_claim.sub != refresh_claim.sub:
            raise InvalidJwtToken('identity_mismatch')

        await self.sessions.blacklist(access_claim.jti, access_claim.time_to_live)
        await self.sessions.blacklist(refresh_claim.jti, refresh_claim.time_to_live)

    async def refresh_tokens(self, body: RefreshRequest) -> TokenClaim:
        logger.info('refreshing JWT tokens...')
        claim = await self.decode_strict(body.refresh_token, expected_type='refresh')
        logger.info(f'refresh for user with ID: {claim.user_id}')
        access_jti = tokens.get_token_jti(body.access_token)

        new_jti = tokens.generate_jti()
        success = await self.sessions.rotate(claim.jti, new_jti, claim.time_to_live)
        if access_jti:
            await self.sessions.blacklist(access_jti, claim.time_to_live)

        if not success:
            await self.sessions.blacklist(claim.jti, claim.time_to_live)
            raise DoubleRotationConflict()

        claim.jti = new_jti
        refresh_token = tokens.encode_jwt_payload(self.jwt_policy, claim.payload())

        access_token, _ = tokens.create_claim(
            self.jwt_policy,
            'access',
            user_id=claim.sub,
            cver=claim.cver,
            role=claim.role,
        )

        return TokenClaim(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            expires_at=datetime.fromtimestamp(claim.exp),
            issued_at=claim.iat,
        )

    async def soft_delete_sessions(self, user_id: uuid.UUID) -> None:
        await self.sessions.incr_cver(str(user_id))

    async def require_role(self, min_role: UserRoles, claim: JwtClaim) -> JwtClaim:
        if claim.role < min_role:
            raise RoleForbidden(claim.role)
        return claim


class OAuth2Token(HTTPBearer):
    """
    Requires a Bearer token in the Authorization header
    """

    def __init__(self) -> None:
        super().__init__(
            description='Bearer authentication with JWT tokens.', auto_error=False
        )

    async def __call__(self, request: Request) -> str:
        auth = await super().__call__(request)
        if not auth or not auth.scheme.lower() == 'bearer':
            raise AuthMissing()
        return auth.credentials
