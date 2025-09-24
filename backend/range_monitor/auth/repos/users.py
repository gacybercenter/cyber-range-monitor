




from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import msgspec
import sqlalchemy as sql
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.db.models import User
from range_monitor.db.repos.sql import SQLReadRepository, SQLWriteRepository
from range_monitor.core.enums import UserRoles

if TYPE_CHECKING:
    from range_monitor.params import TimestampParams


class UserAuth(msgspec.Struct):
    id: str
    username: str
    password_hash: str
    role: UserRoles
    cver: int



class UserReadsRepo(SQLReadRepository[User]):
    model = User

    async def get_username(self, user_id: str) -> str | None:
        '''
        Retrieve the username for a given user ID.

        Parameters
        ----------
        user_id : str

        Returns
        -------
        str | None
            The username if found, otherwise None.
        '''
        user = await self.first_dict(
            sql.select(User.username).
            where(User.id == user_id)
        )
        return user.get('username') if user else None

    async def by_id(self, user_id: str) -> User | None:
        return await self.scalar(
            sql.select(User).
                where(User.id == user_id)
        )

    async def username_unique(
        self,
        username: str,
        *,
        excluding_id: str | None = None
    ) -> bool:
        stmnt = (
            sql.select(User.id).
                distinct().
                where(User.username == username)
        )
        if excluding_id:
            stmnt = stmnt.where(User.id != excluding_id)

        existing = await self.first_dict(stmnt)
        return existing is None

    async def create_query(
        self,
        *,
        with_role: UserRoles | None = None,
        search: str | None = None,
        timestamps: TimestampParams | None = None,
        logged_in_after: datetime | None = None,
    ):
        stmnt = (
            select(User).
            distinct().
            order_by(
                User.username.asc(),
                User.created_at.desc(),
            )
        )

        if with_role:
            stmnt = stmnt.where(User.role == with_role)

        if search:
            stmnt = stmnt.where(
                self.safelike(search, User.username)
            )

        if timestamps:
            stmnt = timestamps.apply(
                stmnt,
                User.created_at,
                User.updated_at
            )


        if logged_in_after:
            stmnt = stmnt.where(User.last_login_at >= logged_in_after)

        count = await self.get_query_total(stmnt)
        return stmnt, count

    async def get_user_auth(self, username: str) -> UserAuth | None:
        stmnt = (
            sql.select(
                User.id,
                User.username,
                User.password_hash,
                User.role,
                User.credential_version.label('cver'),
            ).
            distinct().
            where(User.username == username)
        )
        result = await self.first_dict(stmnt)
        if not result:
            return None
        return UserAuth(**result)



class UserWritesRepo(SQLWriteRepository[User]):
    model = User

    async def create_user(
        self,
        username: str,
        password_hash: str,
        role: UserRoles,
    ) -> User:
        new_user = self.insert(
            username=username,
            password_hash=password_hash,
            role=role,
        )
        await self.transaction(commit=True)
        await self.sync(new_user)
        return new_user

    async def patch_user(
        self,
        user: User,
        params: dict,
    ) -> User | None:
        self.patch(user, **params)


        success = await self.transaction(commit=True)

        if not success:
            return None
        await self.sync(user)
        return user

    async def touch_last_login(self, user_id: str) -> bool:
        stmnt = (
            sql.update(User).
            where(User.id == user_id).
            values(last_login_at=sql.func.now())
        )
        result = await self.db.execute(stmnt)

        if self.was_successful(result):
            await self.transaction(commit=True)
            return True

        return False



class UserRepository:

    def __init__(self, db: AsyncSession) -> None:
        self.read: UserReadsRepo = UserReadsRepo(db)
        self.write: UserWritesRepo = UserWritesRepo(db)

