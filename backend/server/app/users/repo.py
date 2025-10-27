from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from sqlalchemy import Select, Update, func, select, update
from sqlalchemy.orm import load_only

from server.app.users.schema import InternalUser, UserQuery
from server.db import sql_cmds
from server.models import User

if TYPE_CHECKING:
    import uuid
    from datetime import datetime

    from server.db.repos import SQLRepository
    from server.enums import UserRoles


def get_user_filter_clauses(
    *,
    with_role: UserRoles | None = None,
    logged_in_after: datetime | None = None,
    created_by: str | None = None,
) -> list[Any]:
    filters = []
    if with_role:
        filters.append(User.role == with_role)

    if logged_in_after:
        filters.append(User.last_login_at >= logged_in_after)

    if created_by:
        filters.append(User.created_by == created_by)

    return filters


def select_user_auth(
    *, id: uuid.UUID | None = None, username: str | None = None
) -> Select:
    '''
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
    '''
    query = select(
        User.id,
        User.username,
        User.role,
        User.password_hash,
        User.credential_version.label('cver'),
    )

    if id:
        query = query.where(User.id == id)

    if username:
        query = query.where(User.username == username)

    return query


def touch_last_login(user_id: uuid.UUID) -> Update:
    '''
    Updates the last login timestamp for a user.
    '''
    return update(User).where(User.id == user_id).values(last_login_at=func.now())


def incr_credential_version(user_id: uuid.UUID) -> Update:
    '''
    Increments the credential version of a user by 1.
    '''
    return (
        update(User)
        .where(User.id == user_id)
        .values(credential_version=User.credential_version + 1)
    )


async def is_username_unique(
    repo: SQLRepository[User], *, username: str, excluding_id: uuid.UUID | None = None
) -> bool:
    '''
    Check if a username is unique in the database
    with an optional exclusion of a specific user ID.
    '''
    stmnt = select(User.id).where(User.username == username)
    if excluding_id:
        stmnt = stmnt.where(User.id != excluding_id)

    existing = await repo.get_row(stmnt)
    return existing is None


async def filter_users_by(
    repo: SQLRepository[User], query: UserQuery
) -> tuple[Select, int]:
    '''
    Creates a SQLAlchemy Select statement to filter users
    by.
    '''
    filters = get_user_filter_clauses(
        with_role=query.with_role,
        logged_in_after=query.logged_in_after,
        created_by=query.created_by,
    )
    stmnt = (
        select(
            User.id,
            User.username,
            User.role,
            User.last_login_at,
            User.created_by,
            User.credential_version,
        )
        .where(*filters)
        .order_by(User.username)
    )
    total = await repo.count(*filters)
    return stmnt, total


async def get_internal_user(
    repo: SQLRepository[User],
    *,
    user_id: uuid.UUID | None = None,
    username: str | None = None,
) -> InternalUser | None:
    stmnt = select_user_auth(
        id=user_id,
        username=username,
    )
    row = await repo.get_row(stmnt)
    if row is None:
        return None

    return InternalUser(**row)


async def get_username_by_id(
    repo: SQLRepository[User],
    user_id: uuid.UUID,
) -> str | None:
    '''
    Gets only the username of a user by their ID.
    '''
    db_user = await repo.read(
        user_id,
        options=[load_only(User.username)],
    )

    return db_user.username if db_user else None


async def create_db_user(
    users: SQLRepository[User],
    *,
    creator_name: str,
    username: str,
    password_hash: str,
    role: UserRoles,
) -> User:
    '''
    Inserts a new user into the database.
    '''
    new_user = await users.insert(
        username=username,
        password_hash=password_hash,
        role=role,
        created_by=creator_name,
    )
    await users.save()
    await users.db.refresh(new_user)
    return new_user


async def update_db_user(
    repo: SQLRepository[User],
    user: User,
    params: dict,
) -> User:
    sql_cmds.set_model_attrs(user, **params)
    if 'password_hash' in params or 'role' in params:
        user.credential_version += 1

    await sql_cmds.try_save_db(
        repo.db,
        table_name=repo.tablename,
        commit=True,
    )
    await repo.db.refresh(user)
    return user


async def touch_user_id(
    user_id: uuid.UUID, repo: SQLRepository[User], *, mode: Literal['login', 'credential']
) -> bool:
    """
    Touches a user's last login time or increments their
    credential version.
    """
    if mode == 'login':
        stmnt = touch_last_login(user_id)

    elif mode == 'credential':
        stmnt = incr_credential_version(user_id)

    else:
        raise ValueError("Mode must be either 'login' or 'credential'.")

    await repo.exec(f'touch_user_{mode}', stmnt, commit=True)
    return True
