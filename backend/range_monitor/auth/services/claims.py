from datetime import datetime
from typing import NamedTuple, Self

import msgspec
from jose import JWTError, jwt

from range_monitor.core.enums import UserRoles
from range_monitor.security import JwtTokenPolicy


class JwtClaim(msgspec.Struct):
    iss: str
    sub: str
    aud: str
    iat: int
    exp: int
    nbf: int
    jti: str
    token_type: str
    username: str
    role: UserRoles
    cver: int

    @classmethod
    def make(
        cls,
        policy: JwtTokenPolicy,
        token_type: str,
        *,
        user_id: str,
        role: UserRoles,
        username: str,
        cver: int
    ) -> Self:
        now = datetime.now()
        ttl = policy.get_token_ttl(token_type)
        exp = now + ttl
        return cls(
            iss=policy.issuer,
            sub=user_id,
            aud=policy.audience,
            iat=int(now.timestamp()),
            exp=int(exp.timestamp()),
            nbf=int(now.timestamp()),
            jti=policy.generate_jti(),
            token_type=token_type,
            username=username,
            role=role,
            cver=cver
        )

    def payload(self) -> dict:
        return {
            "iss": self.iss,
            "sub": self.sub,
            "aud": self.aud,
            "iat": self.iat,
            "exp": self.exp,
            "nbf": self.nbf,
            "jti": self.jti,
            "token_type": self.token_type,
            "username": self.username,
            "role": self.role.value,
            "cver": self.cver,
        }

    @property
    def time_to_live(self) -> int:
        return max(0, self.exp - int(datetime.now().timestamp()))

    def rotate(
        self,
        *,
        new_jti: str,
        username: str,
    ) -> 'JwtClaim':
        if self.token_type != 'refresh':
            raise ValueError('can only rotate refresh tokens')

        now = datetime.now()
        ttl = datetime.fromtimestamp(self.exp) - now
        exp = now + ttl
        return JwtClaim(
            iss=self.iss,
            sub=self.sub,
            aud=self.aud,
            iat=int(now.timestamp()),
            exp=int(exp.timestamp()),
            nbf=int(now.timestamp()),
            jti=new_jti,
            token_type=self.token_type,
            username=username,
            role=self.role,
            cver=self.cver
        )

class InvalidClaims(Exception):

    def __init__(self, code: str, jti: str | None = None) -> None:
        self.code = code
        self.jti = jti
        super().__init__(self.code)



class TokenPair(NamedTuple):
    access: JwtClaim
    refresh: JwtClaim

class JwtClaimsProvider:

    def __init__(self, policy: JwtTokenPolicy) -> None:
        self._policy: JwtTokenPolicy = policy


    def encode(self, claims: dict) -> str:
        return jwt.encode(
            claims,
            self._policy.key,
            algorithm=self._policy.algorithm,
            headers=self._policy.jwt_headers,
        )

    def decode_strict(self, token: str) -> dict:
        return jwt.decode(
            token,
            self._policy.key,
            algorithms=[self._policy.algorithm],
            options=self._policy.validation_options,
            audience=self._policy.audience,
            issuer=self._policy.issuer,
        )

    def issue(
        self,
        token_type: str,
        *,
        user_id: str,
        role: UserRoles,
        username: str,
        cver: int,
    ) -> tuple[str, JwtClaim]:
        claim = JwtClaim.make(
            self._policy,
            token_type,
            user_id=user_id,
            role=role,
            username=username,
            cver=cver
        )
        token = self.encode(claim.payload())
        return token, claim

    def verify_claim(
        self,
        claims: dict,
        *,
        expected_type: str,
    ) -> JwtClaim:
        '''
        Validates the claim into type safe object.
        The `cver` is the credential version, which is incremented
        anytime the user's role or permissions change, forcing
        any previously issued tokens to become stale.

        Parameters
        ----------
        expected_type : str
        current_cver : int
        claims : dict

        Returns
        -------
        JwtClaim

        Raises
        ------
        InvalidClaims
        '''
        try:
            claim = JwtClaim(**claims)
        except msgspec.ValidationError:
            raise InvalidClaims(
                code='malformed_claims',
                jti=claims.get('jti')
            )

        if claim.token_type != expected_type:
            raise InvalidClaims(
                code='invalid_token_type',
                jti=claim.jti
            )

        return claim

    def extract_jti(self, token: str) -> str | None:
        try:
            decoded = jwt.get_unverified_claims(token)
        except JWTError:
            return None
        return decoded.get('jti', None)