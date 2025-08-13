from api.exceptions.http import HTTPForbidden
from app.api.schemas.users import UserModel
from app.infrastructure.security.roles import Role


class RoleChecker:
    def __init__(self, min_role: Role) -> None:
        self.min_role: Role = min_role

    async def check_user_role(self, user: UserModel) -> UserModel:
        """Checks if the user's role is at least the minimum required role."""
        if user.role < self.min_role:
            raise HTTPForbidden(
                'You do not have the required permissions to perform this action.'
            )
        return user


class ReadOnlyRequired(RoleChecker):
    """A role checker that requires the user to have at least read permissions."""

    def __init__(self) -> None:
        super().__init__(Role.READ_ONLY)


class AdminRequired(RoleChecker):
    def __init__(self) -> None:
        super().__init__(Role.ADMIN)


class UserRequired(RoleChecker):
    """A role checker that requires the user to have at least user permissions."""

    def __init__(self) -> None:
        super().__init__(Role.USER)
