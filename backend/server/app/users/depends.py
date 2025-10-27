from typing import Annotated

from fastapi import Depends

from server.app.auth.depends import (
    AccessTokenDep,
    AuthServiceDep,
    TokenStoreDep,
)
from server.app.auth.service import InternalUser
from server.app.depends import DatabaseDep
from server.app.errors.http import ForbiddenError
from server.app.users.service import UsersService
from server.db.repos import SQLRepository
from server.enums import UserRoles
from server.models import User


async def get_users_repo(db: DatabaseDep) -> SQLRepository[User]:  # noqa: RUF029
    return SQLRepository(
        db=db,
        model=User,
    )


UsersRepoDep = Annotated[SQLRepository[User], Depends(get_users_repo)]


async def get_users_service(  # noqa: RUF029
    users: UsersRepoDep,
    tokens: TokenStoreDep,
) -> UsersService:
    return UsersService(users=users, tokens=tokens)


UsersServiceDep = Annotated[UsersService, Depends(get_users_service)]


class AuthenticatedUser:
    def __init__(self, min_role: UserRoles = UserRoles.GUEST) -> None:
        self.min_role = min_role

    async def __call__(
        self,
        user: UsersServiceDep,
        auth: AuthServiceDep,
        access_token: AccessTokenDep,
    ) -> InternalUser:
        await auth.require_role(self.min_role, access_token)

        token_user = await user.get_token_user(access_token.sub)
        if not token_user:
            await auth.tokens.delete_user_tokens(access_token.sub)
            raise ForbiddenError('user_no_longer_exists')

        return token_user


AuthorizedGuest = AuthenticatedUser()
AuthorizedUser = AuthenticatedUser(min_role=UserRoles.USER)
AuthorizedAdmin = AuthenticatedUser(min_role=UserRoles.ADMIN)

GuestRequired = Annotated[InternalUser, Depends(AuthorizedGuest)]
UserRequired = Annotated[InternalUser, Depends(AuthorizedUser)]
AdminRequired = Annotated[InternalUser, Depends(AuthorizedAdmin)]
