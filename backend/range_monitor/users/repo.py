from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import Select, Update, func, select, update

from range_monitor.core.enums import UserRoles
from range_monitor.infra import sql_cmds
from range_monitor.infra.repos import SQLRepository
from range_monitor.users.models import User


def _filter_users_by(
    *,
    with_role: UserRoles | None = None,
    search: str | None = None,
    logged_in_after: datetime | None = None,
    created_by: str | None = None,
) -> Select:
    stmnt = (
        select(User).
        distinct().
        order_by(User.username.asc())
    )

    if with_role:
        stmnt = stmnt.where(User.role == with_role)

    if search:
        like_str = sql_cmds.esc_like(f'%{search}%')
        stmnt = stmnt.where(
            User.username.ilike(like_str, escape='\\')
        )

    if logged_in_after:
        stmnt = stmnt.where(User.last_login_at >= logged_in_after)

    if created_by:
        stmnt = stmnt.where(User.created_by == created_by)

    return stmnt



def _select_user_auth(
    *,
    id: uuid.UUID | None = None,
    username: str | None = None
) -> Select:
    query = (
        select(
            User.id,
            User.username,
            User.role,
            User.password_hash,
            User.credential_version.label('cver'),
        ).
        distinct()
    )

    if id:
        query = query.where(User.id == id)

    if username:
        query = query.where(User.username == username)

    return query


def _update_last_login(user_id: uuid.UUID) -> Update:
    return (
        update(User).
        where(User.id == user_id).
        values(last_login_at=func.now())
    )


def _select_by_creator(username: str) -> Select:
    return (
        select(User).
        where(User.created_by == username).
        order_by(User.username.asc())
    )


def _incr_credential_version(user_id: uuid.UUID) -> Update:
    return (
        update(User).
        where(User.id == user_id).
        values(credential_version=User.credential_version + 1)
    )


class UserRepository(SQLRepository[User]):
    model = User

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self.first_orm(
            select(User).
            where(User.id == user_id)
        )

    async def is_username_unique(
        self,
        username: str,
        *,
        excluding_id: uuid.UUID | None = None
    ) -> bool:
        stmnt = (
            select(User.id).
            where(User.username == username)
        )
        if excluding_id:
            stmnt = stmnt.where(User.id != excluding_id)

        existing = await self.first_row(stmnt)
        return existing is None


    async def filter_by(
        self,
        *,
        with_role: UserRoles | None = None,
        search: str | None = None,
        logged_in_after: datetime | None = None,
        created_by: str | None = None,
    ) -> tuple[Select, int]:
        stmnt = _filter_users_by(
            with_role=with_role,
            search=search,
            logged_in_after=logged_in_after,
            created_by=created_by,
        )
        total = await self.count_rows(stmnt)
        return stmnt, total


    async def edit_user(self, user: User, params: dict) -> None:
        sql_cmds.patch_db_model(user, **params)

        if 'password_hash' in params or 'role' in params:
            user.credential_version += 1

        await sql_cmds.try_save_db(
            self.db,
            table_name=self.tablename,
            commit=True,
        )

        await self.db.refresh(user)


    async def touch_last_login(self, user_id: uuid.UUID) -> None:
        await self.db.execute(_update_last_login(user_id))
        await self.save(commit=True)


    async def bump_credential_version(self, user_id: uuid.UUID) -> None:
        await self.db.execute(_incr_credential_version(user_id))
        await self.save(commit=True)


    async def list_users_created_by(self, username: str) -> AsyncGenerator[User, None]:
        stmnt = _select_by_creator(username)
        async for model in self.stream_orms(stmnt):
            yield model


    async def get_internal_user(
        self,
        user_id: uuid.UUID | None = None,
        username: str | None = None,
    ) -> dict | None:
        '''
        Fetch user authorization details by user_id or username.
        One or the other must be provided.

        Parameters
        ----------
        user_id : uuid.UUID | None, optional
        username : str | None, optional

        Returns
        -------
        dict | None

        Raises
        ------
        ValueError
        '''
        if not user_id and not username:
            raise ValueError('Either user_id or username must be provided.')

        stmnt = _select_user_auth(id=user_id, username=username)
        return await self.first_row(stmnt)