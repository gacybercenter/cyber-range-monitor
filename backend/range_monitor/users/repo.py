from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Select, Update, func, select, update

from range_monitor.core.enums import UserRoles
from range_monitor.infra import sql_cmds
from range_monitor.infra.repos import SQLRepository
from range_monitor.users.models import User


def _filter_users_by(
    *,
    with_role: UserRoles | None = None,
    logged_in_after: datetime | None = None,
    created_by: str | None = None,
) -> Select:
    """
    Builds a filtered query for users based on the provided filters
    """
    stmnt = select(User).distinct().order_by(User.username.asc())

    if with_role:
        stmnt = stmnt.where(User.role == with_role)

    if logged_in_after:
        stmnt = stmnt.where(User.last_login_at >= logged_in_after)

    if created_by:
        stmnt = stmnt.where(User.created_by == created_by)

    return stmnt


def _select_user_auth(
    *, id: uuid.UUID | None = None, username: str | None = None
) -> Select:
    """
    Selects user authentication details by either ID or username
    to be converted to `InternalUser`

    Parameters
    ----------
    id : uuid.UUID | None, optional
        _description_, by default None
    username : str | None, optional
        _description_, by default None

    Returns
    -------
    Select
    """
    query = select(
        User.id,
        User.username,
        User.role,
        User.password_hash,
        User.credential_version.label('cver'),
    ).distinct()

    if id:
        query = query.where(User.id == id)

    if username:
        query = query.where(User.username == username)

    return query


def _update_last_login(user_id: uuid.UUID) -> Update:
    """
    Updates the last login timestamp of a user to the current time.

    Parameters
    ----------
    user_id : uuid.UUID

    Returns
    -------
    Update
    """
    return update(User).where(User.id == user_id).values(last_login_at=func.now())


def _incr_credential_version(user_id: uuid.UUID) -> Update:
    """
    Increments the credential version of a user by 1.
    """
    return (
        update(User)
        .where(User.id == user_id)
        .values(credential_version=User.credential_version + 1)
    )


class UserRepository(SQLRepository[User]):
    """
    Abstraction for common user sql-queries
    """

    model = User

    async def get(self, user_id: uuid.UUID) -> User | None:
        """
        Gets a user by it's ID
        """
        return await self.first_orm(select(User).where(User.id == user_id))

    async def is_username_unique(
        self, username: str, *, excluding_id: uuid.UUID | None = None
    ) -> bool:
        """
        Checks if a username is unique with an optional
        parameter to exclude a specific user ID.
        """
        stmnt = select(User.id).where(User.username == username)
        if excluding_id:
            stmnt = stmnt.where(User.id != excluding_id)

        existing = await self.first_row(stmnt)
        return existing is None

    async def list_by(
        self,
        *,
        with_role: UserRoles | None = None,
        logged_in_after: datetime | None = None,
        created_by: str | None = None,
    ) -> tuple[Select, int]:
        """
        Builds a filtered query for users based on the provided criteria.
        """
        stmnt = _filter_users_by(
            with_role=with_role,
            logged_in_after=logged_in_after,
            created_by=created_by,
        )
        total = await self.count_rows(stmnt)
        return stmnt, total

    async def patch(self, user: User, params: dict) -> None:
        """
        Edits a user with the provided parameters, when `password_hash` or `role`
        change the `credential_version` is incremented.

        Parameters
        ----------
        user : User
        params : dict
        """
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
        """
        Updates the last login timestamp of a user to the current time.

        Parameters
        ----------
        user_id : uuid.UUID
        """
        await self.db.execute(_update_last_login(user_id))
        await self.save(commit=True)

    async def bump_credential_version(self, user_id: uuid.UUID) -> None:
        """
        Increments the credential version of a user by 1.

        Parameters
        ----------
        user_id : uuid.UUID
        """
        await self.db.execute(_incr_credential_version(user_id))
        await self.save(commit=True)

    async def fetchuser(
        self,
        *,
        user_id: uuid.UUID | None = None,
        username: str | None = None,
    ) -> dict | None:
        """
        Gets the `InternalUser` dictionary scheme to be converted to

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
        """
        if not user_id and not username:
            raise ValueError('Either user_id or username must be provided.')

        stmnt = _select_user_auth(id=user_id, username=username)
        return await self.first_row(stmnt)
