




from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from range_monitor.auth.errors import InvalidJwtToken, RoleForbiddenError
from range_monitor.auth.repos.claims import ClaimsBackend
from range_monitor.auth.repos.users import UserRepository
from range_monitor.auth.services.claims import JwtClaim, JwtClaimsProvider
from range_monitor.auth.services.passwords import PasswordService
from range_monitor.auth.services.tokens import TokenService
from range_monitor.auth.services.user import UserService
from range_monitor.depends import DatabaseDep, RedisDep, SecurityPolicyDep
from range_monitor.core.enums import UserRoles


async def get_claims_backend(redis: RedisDep) -> ClaimsBackend:
    return ClaimsBackend(redis)


async def get_claims_provider(security_policy: SecurityPolicyDep) -> JwtClaimsProvider:
    return JwtClaimsProvider(security_policy.jwt_token)

async def get_users_repo(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)

async def get_password_service(security_policy: SecurityPolicyDep) -> PasswordService:
    return PasswordService(security_policy.passwords)

async def get_token_service(
    policy: SecurityPolicyDep,
    claims_backend: ClaimsBackend = Depends(get_claims_backend),
) -> TokenService:
    return TokenService(
        policy=policy.jwt_token,
        claims=claims_backend
    )

async def get_user_service(
    db: DatabaseDep,
    security_policy: SecurityPolicyDep
) -> UserService:
    return UserService(
        db=db,
        password_policy=security_policy.passwords
    )

ClaimsBackendDep = Annotated[ClaimsBackend, Depends(get_claims_backend)]
ClaimsProviderDep = Annotated[JwtClaimsProvider, Depends(get_claims_provider)]
UsersRepoDep = Annotated[UserRepository, Depends(get_users_repo)]
PasswordServiceDep = Annotated[PasswordService, Depends(get_password_service)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]

class TokenBearerSecurity(HTTPBearer):

    def __init__(
        self,
        *,
        token_type: str = 'access'
    ):
        super().__init__(
            scheme_name=self.__class__.__name__,
            description=(
                f'Ensures the user provides a valid {token_type} JWT token.'
            ),
            auto_error=False
        )
        self.token_type = token_type

    async def __call__(self, request: Request, token_service: TokenService) -> JwtClaim:

        credentials = await super().__call__(request)
        if not credentials or credentials.scheme.lower() != 'bearer':
            raise InvalidJwtToken(
                detail='not_authenticated',
                token_type=self.token_type
            )

        token = credentials.credentials
        claim = await token_service.verify_token(
            token=token,
            token_type=self.token_type
        )
        return claim

AccessTokenBearer = TokenBearerSecurity(token_type='access')
RefreshTokenBearer = TokenBearerSecurity(token_type='refresh')

AccessTokenDep = Annotated[JwtClaim, Depends(AccessTokenBearer)]
RefreshTokenDep = Annotated[JwtClaim, Depends(RefreshTokenBearer)]


class RoleRequired:
    '''
    Enforces both a valid access token and a minimum user role
    per request.
    '''
    def __init__(self, min_role: UserRoles) -> None:
        self.min_role = min_role

    async def __call__(self, claim: AccessTokenDep) -> JwtClaim:
        if claim.role < self.min_role:
            raise RoleForbiddenError()
        return claim

AdminRoleRequired = RoleRequired(min_role=UserRoles.ADMIN)
UserRoleRequired = RoleRequired(min_role=UserRoles.USER)
GuestRoleRequired = RoleRequired(min_role=UserRoles.GUEST)

AdminRoleDep = Annotated[JwtClaim, Depends(AdminRoleRequired)]
UserRoleDep = Annotated[JwtClaim, Depends(UserRoleRequired)]
GuestRoleDep = Annotated[JwtClaim, Depends(GuestRoleRequired)]

