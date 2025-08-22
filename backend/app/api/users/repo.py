from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.sql_repo import SqlRepository

from .model import Role, User


class RoleRepo(SqlRepository[Role]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Role)


    async def get_by_id(self, role_id: int) -> Role | None:
        return await self.get(Role.id == role_id)

    async def get_by_name(self, name: str) -> Role | None:
        return await self.get(Role.name == name)

    async def role_name_to_id(self, name: str) -> str | None:
        query = select(Role.id).where(Role.name == name)
        result = await self._session.execute(query)
        role_id = result.scalar_one_or_none()
        return str(role_id) if role_id is not None else None

    async def get_role_scopes(self, role_name: str) -> list[str]:
        query = select(Role.scopes_json).where(Role.name == role_name)
        result = await self._session.execute(query)
        scopes_json = result.scalar_one_or_none()
        if scopes_json is None:
            return []
        try:
            scopes = scopes_json.split(',')
            return [scope.strip() for scope in scopes if scope.strip()]
        except Exception:
            return []

class UserRepo(SqlRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        self.roles: RoleRepo = RoleRepo(session)
        super().__init__(session, User)

    async def create_user(self, **kwargs) -> User | None:
        if not (role := kwargs.pop('role', None)):
            return None

        if not (role_id := await self.roles.role_name_to_id(role)):
            return None

        kwargs['role_id'] = role_id
        return await self.create(**kwargs)

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.get(User.id == user_id)

    async def _set_active(self, user_id: UUID, active: bool) -> bool:
        if not (existing_user := await self.get_by_id(user_id)):
            return False
        existing_user.is_active = active
        await self.sync_db(commit=True)
        return True

    async def activate(self, user_id: UUID) -> bool:
        '''Sets `is_active` to True for the user.'''
        return await self._set_active(user_id, True)

    async def deactivate(self, user_id: UUID) -> bool:
        return await self._set_active(user_id, False)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get(User.username == username)

    async def update_user(
        self,
        user: User,
        *,
        params: dict
    ) -> User | None:
        if role := params.get('role'):
            if not (role_id := await self.roles.role_name_to_id(role)):
                return None
            params['role_id'] = role_id
        return await self.update(user, params, commit=True)

    async def delete_user(self, user: User) -> bool:
        return await self.delete(user, commit=True)

    async def get_users_with_role(self, role_id: UUID) -> list[User]:
        return await self.all(
            select(User).where(User.role_id == role_id)
        )

    async def get_role_names(self) -> list[str]:
        """
        Returns a list of all role names.
        """
        query = select(Role.name)
        result = await self._session.execute(query)
        return [row[0] for row in result.fetchall() if row[0] is not None]

    async def username_taken(self, username: str) -> bool:
        """
        Checks if a username is already taken.
        """
        return await self.exists(User.username == username)

