from typing import NamedTuple

from sqlalchemy import Select, delete, select

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.depends import DatabaseDep
from range_monitor.errors import ResourceNotFound
from range_monitor.params import PageParams, TimestampParams
from range_monitor.users.roles import UserRoles

from .model import User


class UserQuery(NamedTuple):
    total: int
    query: Select


class UserRepo(SqlRepo[User]):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        stmnt = select(User).where(User.username == username)
        return await self.one_or_none(stmnt)

    async def is_username_unique(self, username: str) -> bool:
        stmnt = select(User).where(User.username == username)
        result = await self.first(stmnt)
        return result is None

    async def delete_user(self, user_id: str) -> None:
        statement = delete(User).where(User.id == user_id)
        result = await self.db.execute(statement)
        if result.rowcount == 0:
            raise ResourceNotFound(f'User with ID {user_id} not found')
        await self.save()

    async def read_by_id(self, user_id: str) -> User:
        '''
        Retrieve a user by their ID.

        Parameters
        ----------
        user_id : str

        Returns
        -------
        User

        Raises
        ------
        ResourceNotFound
            _If the user does not exist_
        '''
        if not (user := await self.get(user_id)):
            raise ResourceNotFound(f'User with ID {user_id} not found')
        return user

    async def query(
        self,
        *,
        page: PageParams,
        timestamp: TimestampParams,
        with_role: UserRoles | None = None,
    ) -> UserQuery:
        '''
        Paginates users with optional filtering by role and timestamps
        returing the total count and the query itself which has been
        paginated

        Parameters
        ----------
        page : PageParams
        timestamp : TimestampParams
        with_role : UserRoles | None, optional
            _The role to filter by_, by default None

        Returns
        -------
        UserQuery
            _The prepared query_
        '''
        stmnt = select(User).order_by(User.username.asc())
        if with_role:
            stmnt = stmnt.where(User.role == with_role)
        stmnt = timestamp.apply(stmnt, User.created_at, User.updated_at)
        total = await self.get_query_total(stmnt)

        return UserQuery(
            total=total,
            query=stmnt.limit(page.limit).offset(page.offset),
        )


async def get_user_repo(db: DatabaseDep) -> UserRepo:
    return UserRepo(db)