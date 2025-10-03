from fastapi import Depends, Security
from typing_extensions import Annotated

from range_monitor.auth.repo import SessionRepository
from range_monitor.auth.schema import JwtClaim
from range_monitor.auth.service import AuthenticationService, OAuth2Token
from range_monitor.core.enums import UserRoles
from range_monitor.depends import ContextRequired, RedisDep


async def get_auth_service(
    context: ContextRequired,
    redis: RedisDep
) -> AuthenticationService:
    sessions = SessionRepository(redis)
    return AuthenticationService(
        sessions=sessions,
        jwt_policy=context.jwt_policy,
    )

AuthServiceDep = Annotated[
    AuthenticationService,
    Depends(get_auth_service)
]

oauth2_token = OAuth2Token()

TokenRequired = Annotated[str, Security(oauth2_token)]

class TokenClaim:
    def __init__(self, claim_type: str) -> None:
        self.claim_type: str = claim_type

    async def __call__(
        self,
        token: TokenRequired,
        auth_service: AuthServiceDep
    ) -> JwtClaim:
        return await auth_service.decode_strict(token, self.claim_type)


AccessTokenClaim = TokenClaim('access')
RefreshTokenClaim = TokenClaim('refresh')

AccessTokenDep = Annotated[JwtClaim, Depends(AccessTokenClaim)]
RefreshTokenDep = Annotated[JwtClaim, Depends(RefreshTokenClaim)]


class RoleRequired:
    def __init__(self, min_role: UserRoles) -> None:
        self.min_role: UserRoles = min_role

    async def __call__(
        self,
        access_token: TokenRequired,
        auth_service: AuthServiceDep
    ) -> JwtClaim:
        claim = await auth_service.decode_strict(access_token, 'access')
        return await auth_service.require_role(
            min_role=self.min_role,
            claim=claim
        )

AdminRequired = RoleRequired(UserRoles.ADMIN)
UserRequired = RoleRequired(UserRoles.USER)
GuestRequired = RoleRequired(UserRoles.GUEST)

AdminClaimDep = Annotated[JwtClaim, Security(AdminRequired)]
UserClaimDep = Annotated[JwtClaim, Security(UserRequired)]
GuestClaimDep = Annotated[JwtClaim, Security(GuestRequired)]