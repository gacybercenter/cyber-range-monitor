from enum import IntEnum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.sql_repo import SqlRepository

from .model import Role, User


class UserReadMode(IntEnum):
    DEFAULT = 0
    DETAILED = 1
    COMPLETE = 2



class RoleRepo(SqlRepository[Role]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Role)


    async def create_role(
        self,
        name: str,
        description: str | None = None
    ) -> Role:
        return await self.create({
            'name': name,
            'description': description
        })

    async def get_by_id(self, role_id: int) -> Role | None:
        return await self.get(Role.id == role_id)

    async def get_by_name(self, name: str) -> Role | None:
        return await self.get(Role.name == name)

    async def role_name_to_id(self, name: str) -> str | None:
        query = select(Role.id).where(Role.name == name)
        result = await self._session.execute(query)
        role_id = result.scalar_one_or_none()
        return str(role_id) if role_id is not None else None


class UserRepo(SqlRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        self.roles: RoleRepo = RoleRepo(session)
        super().__init__(session, User)

    async def create_user(
        self,
        username: str,
        password_hash: str,
        role: str,
        is_active: bool = True,
    ) -> User | None:
        if not (role_id := await self.roles.role_name_to_id(role)):
            return None
        return await self.create({
            'username': username,
            'password_hash': password_hash,
            'role_id': role_id,
            'is_active': is_active
        }, commit=False)

    async def get_by_id(self, user_id: str) -> User | None:
        return await self.get(User.id == user_id)

    async def _set_active(self, user_id: str, active: bool) -> bool:
        if not (existing_user := await self.get_by_id(user_id)):
            return False
        existing_user.is_active = active
        await self.sync_db(commit=True)
        return True

    async def activate(self, user_id: str) -> bool:
        '''Sets `is_active` to True for the user.'''
        return await self._set_active(user_id, True)

    async def deactivate(self, user_id: str) -> bool:
        return await self._set_active(user_id, False)

    async def get_by_username(self, username: str) -> User | None:
        return await self.get(User.username == username)

    async def update_user(
        self,
        user_id: str,
        *,
        params: dict
    ) -> User | None:
        if not (existing_user := await self.get_by_id(user_id)):
            return None

        if role := params.get('role'):
            if not (role_id := await self.roles.role_name_to_id(role)):
                return None
            params['role_id'] = role_id
        return await self.update(existing_user, params, commit=True)

    async def delete_user(self, user_id: str) -> bool:
        if not (existing_user := await self.get_by_id(user_id)):
            return False
        return await self.delete(existing_user, commit=True)

    async def get_users_with_role(
        self,
        role: str
    ) -> list[User]:
        if not (role_id := await self.roles.role_name_to_id(role)):
            return []
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
