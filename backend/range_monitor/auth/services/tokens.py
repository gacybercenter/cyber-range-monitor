
from contextlib import asynccontextmanager
from datetime import datetime
from jose import ExpiredSignatureError, JWTError

from range_monitor.auth.errors import InvalidJwtToken, TokenRotationError
from range_monitor.auth.repos.claims import ClaimsBackend, RotationError
from range_monitor.auth.schema import AuthClaim, TokenDetails, TokenUser
from range_monitor.auth.services.claims import (
    InvalidClaims,
    JwtClaim,
    JwtClaimsProvider,
)
from range_monitor.core.enums import UserRoles
from range_monitor.security import JwtTokenPolicy


class TokenService:


    def __init__(
        self,
        *,
        policy: JwtTokenPolicy,
        claims: ClaimsBackend
    ) -> None:
        self.provider: JwtClaimsProvider = JwtClaimsProvider(policy)
        self.policy: JwtTokenPolicy = policy
        self.claims: ClaimsBackend = claims

    async def create_claims(
        self,
        *,
        user_id: str,
        role: UserRoles,
        cver: int,
        username: str
    ) -> AuthClaim:
        access_token, access_claim = self.provider.issue(
            'access',
            user_id=user_id,
            role=role,
            username=username,
            cver=cver
        )
        refresh_token, refresh_claim = self.provider.issue(
            'refresh',
            user_id=user_id,
            role=role,
            username=username,
            cver=cver
        )
        await self.claims.save(refresh_claim)
        return AuthClaim(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            expires_in=access_claim.time_to_live,
        )

    async def decode_token(self, token: str, token_type: str) -> JwtClaim:
        '''
        Decodes and verifies the token. If the token decodes properly,
        but fails to parse; the claim is blacklisted. No redis verification
        is done at this step.

        Parameters
        ----------
        token : str
        type_ : str

        Returns
        -------
        JwtClaim

        Raises
        ------
        UnauthorizedAccess
        '''

        try:
            claim_dict = self.provider.decode_strict(token)
        except ExpiredSignatureError:
            raise InvalidJwtToken('token_expired', token_type)
        except JWTError:
            raise InvalidJwtToken('token_invalid', token_type)

        try:
            claim = self.provider.verify_claim(
                claim_dict,
                expected_type=token_type
            )
        except InvalidClaims as exc:
            # the provided token would only fail here
            # if it was tampered with by an attacker
            if jti := exc.jti:
                ttl = self.policy.get_token_ttl(token_type).total_seconds()
                await self.claims.blacklist_jti(jti, int(ttl))

            raise InvalidJwtToken(exc.code, token_type) from exc

        return claim

    async def verify_token(self, token: str, *, token_type: str) -> JwtClaim:
        claim = await self.decode_token(token, token_type)

        if err := await self.claims.get_claims_error(claim):
            raise InvalidJwtToken(err, token_type)

        return claim


    async def refresh_claim(
        self,
        old_refresh: JwtClaim,
        access_token: str,
        *,
        username: str # since username can become stale, one col db lookup is better
    ) -> AuthClaim:
        if not (access_jti := self.provider.extract_jti(access_token)):
            await self.claims.blacklist_jti(
                old_refresh.jti,
                old_refresh.time_to_live
            )
            raise TokenRotationError('original_access_jti_missing')

        rotated_refresh = old_refresh.rotate(
            new_jti=self.policy.generate_jti(),
            username=username
        )

        try:
            await self.claims.rotate_claim(
                old_jti=old_refresh.jti,
                old_access_jti=access_jti,
                new_claim=rotated_refresh,
            )
        except RotationError as exc:
            raise TokenRotationError(exc.code)

        access_token, access_claim = self.provider.issue(
            'access',
            user_id=rotated_refresh.sub,
            role=rotated_refresh.role,
            username=username,
            cver=rotated_refresh.cver
        )
        refresh_token = self.provider.encode(rotated_refresh.payload())

        return AuthClaim(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type='bearer',
            expires_in=access_claim.time_to_live,
        )

    async def revoke_tokens(self, access_token: str, refresh_token: str) -> None:

        access_claim = await self.verify_token(
            access_token,
            token_type='access'
        )
        refresh_claim = await self.verify_token(
            refresh_token,
            token_type='refresh'
        )
        await self.claims.revoke_claim(
            claim=refresh_claim,
            access_jti=access_claim.jti
        )

    async def cache_cver(self, user_id: str, cver: int) -> None:
        await self.claims.ensure_cver(user_id, cver)

    async def inspect(self, claim: JwtClaim) -> TokenDetails:

        issued_at = datetime.fromtimestamp(claim.iat)
        expires_at = datetime.fromtimestamp(claim.exp)

        user = TokenUser(
            user_id=claim.sub,
            username=claim.username,
            cver=claim.cver,
            role=claim.role,
        )

        return TokenDetails(
            time_to_live=claim.time_to_live,
            issued_at=issued_at,
            expires_at=expires_at,
            user=user
        )

    @asynccontextmanager
    async def blacklist_on_error(self, claim: JwtClaim):
        '''
        Context manager to automatically blacklist the given claim's jti,
        in must use cases. This should never occur but exists as a safety
        mechanism nonetheless.

        Parameters
        ----------
        claim : JwtClaim
        '''
        try:
            yield
        except Exception:
            await self.claims.blacklist_jti(
                claim.jti,
                claim.time_to_live
            )
            raise