from enum import IntEnum
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.users import UserQueryParams
from app.infrastructure.repos import SqlPageResult, SqlRepository

from .model import Role, User


class UserReadMode(IntEnum):
    DEFAULT = 0
    DETAILED = 1
    COMPLETE = 2


class UserRepository(SqlRepository[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    def _user_select(
        self,
        user_read: UserReadMode = UserReadMode.DEFAULT,
    ) -> Select:
        if user_read == UserReadMode.DETAILED:
            return select(
                User.id,
                User.username,
                User.role,
                User.created_at,
                User.updated_at,
            )
        elif user_read == UserReadMode.COMPLETE:
            return select(User)
        else:
            return select(User.id, User.username, User.role)

    def _role_based_select(
        self,
        read_mode: UserReadMode,
        reader_role: Role,
    ) -> Select:
        return self._user_select(read_mode).where(User.role <= reader_role)

    def _get_by(self, read_type: UserReadMode, where_clause: Any) -> Select:
        return self._user_select(read_type).where(where_clause)

    async def get_by_id(
        self,
        user_id: str,
        *,
        user_read: UserReadMode = UserReadMode.DEFAULT,
    ) -> User | None:
        """Get a user by ID with specified read level."""

        stmnt = self._get_by(
            read_type=user_read,
            where_clause=User.id == user_id,
        )
        return await self.first(stmnt)

    async def get_by_username(
        self,
        username: str,
        *,
        user_read: UserReadMode = UserReadMode.DEFAULT,
    ) -> User | None:
        """Get a user by username with specified read level."""

        stmnt = self._get_by(
            read_type=user_read,
            where_clause=User.username == username,
        )
        return await self.first(stmnt)

    async def username_exists(
        self,
        username: str,
    ) -> bool:
        """Check if a username exists in the database."""
        stmnt = select(User.id).where(User.username == username)
        return await self.exists(stmnt)

    async def update_user_by_id(
        self,
        options: dict[str, Any],
        user_id: str,
    ) -> User | None:
        existing_user = await self.get_by_id(
            user_id=user_id,
            user_read=UserReadMode.COMPLETE,
        )
        if not existing_user:
            return None

        await self.update(existing_user, options)

        return existing_user

    async def delete_by_id(self, user_id: str) -> bool:
        existing_user = await self.get_by_id(
            user_id=user_id,
            user_read=UserReadMode.COMPLETE,
        )
        if not existing_user:
            return False

        await self.delete(existing_user)
        return True

    async def paginate_users(
        self, *, read_mode: UserReadMode, options: UserQueryParams, reader_role: Role
    ) -> SqlPageResult[User]:
        stmnt = self._role_based_select(
            read_mode=read_mode,
            reader_role=reader_role,
        )

        if read_mode >= UserReadMode.DETAILED:
            if options.created_before:
                stmnt = stmnt.where(User.created_at < options.created_before)

            if options.created_after:
                stmnt = stmnt.where(User.created_at > options.created_after)

            if options.updated_before:
                stmnt = stmnt.where(User.updated_at < options.updated_before)

            if options.updated_after:
                stmnt = stmnt.where(User.updated_at > options.updated_after)

        if options.role:
            stmnt = stmnt.where(User.role == options.role)

        col = User.id
        if options.sort_by == 'username':
            col = User.username

        elif options.sort_by == 'role':
            col = User.role

        stmnt = self.order_by(
            stmnt,
            col=col,
            direction=options.sort_order,
        )

        return await self.paginate(
            statement=stmnt,
            page=options.page,
            page_size=options.page_size,
        )
