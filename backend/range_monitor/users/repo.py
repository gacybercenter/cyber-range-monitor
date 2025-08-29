from typing import NamedTuple
from uuid import UUID

from sqlalchemy import Select, delete, select

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.depends import DatabaseDep
from range_monitor.errors import ResourceNotFound
from range_monitor.users.roles import UserRoles

from .model import User


class UserPage(NamedTuple):
    total: int
    users: list[dict]


class UserRepo(SqlRepo[User]):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        existing_user = await self.db.scalar(
            select(User).where(User.username == username)
        )
        return existing_user

    async def is_username_unique(self, username: str) -> bool:
        stmnt = self.select(User.username == username, cols=(User.id,))
        result = await self.one_or_none(stmnt)
        return result is None

    def query(
        self,
        *,
        with_role: UserRoles | None,
    ) -> Select:
        query = select(User)
        if with_role:
            query = query.where(User.role == with_role)

        return query.order_by(
            User.username.asc(),
        )

    async def delete_user(self, user_id: UUID) -> None:
        statement = delete(User).where(User.id == user_id)
        result = await self.db.execute(statement)
        if result.rowcount == 0:
            raise ResourceNotFound(f'User with ID {user_id} not found')
        await self.save()


async def get_user_repo(db: DatabaseDep) -> UserRepo:
    return UserRepo(db)