
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.core.enums import RoleLevelMap, UserRoles
from range_monitor.db.base import SqlModel
from range_monitor.db.uuid_type import MappedPrimaryKeyID


class User(SqlModel):
    '''
    Represents the `users` table in the database.

    Columns
    -------
    id : str
        Unique identifier for the user, primary key (UUID format).
    username : str
        Unique username for the user, indexed.
    password_hash : str
        Hashed password for authentication.
    role : UserRoles
        Role assigned to the user, comparable using the hybrid property.
    credential_version : int
        Version of the user credentials, incremented on password or role change
        enforced by a database trigger.
    last_login_at : datetime | None
        Timestamp of the last login, nullable if never logged in.
    created_at : datetime
        Timestamp when the user was created, set automatically.
    updated_at : datetime
        Timestamp when the user was last updated, set automatically.

    Triggers
    --------
    - Before update of `role` or `password_hash`, increment `credential_version`
    enforced at the database level.
    '''

    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = MappedPrimaryKeyID()

    username: Mapped[str] = mapped_column(
        sa.String(128),
        nullable=False,
        unique=True,
        index=True,
        doc='Unique username for the user, indexed'
    )

    password_hash: Mapped[str] = mapped_column(
        sa.String(),
        nullable=False,
        doc='Hashed password for authentication'
    )

    role: Mapped[UserRoles] = mapped_column(
        sa.Enum(UserRoles),
        default=UserRoles.USER,
        nullable=False,
        index=True,
        doc='Role assigned to the user, comparable using the hybrid property.'
    )

    credential_version: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        doc='Version of the user credentials, incremented on password or role change.'
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc='Timestamp of the last login, nullable if never logged in.'
    )

    @hybrid_property
    def role_level(self) -> int:  # type: ignore[override]
        return self.role.level

    @role_level.expression
    def role_level(cls):
        return sa.case(
            RoleLevelMap,
            value=cls.role,
            else_=0
        )

    __mapper_args__ = {
        'order_by': username.asc()
    }

    __table_args__ = (
        sa.CheckConstraint(
            'length(username) >= 3',
            name='username_min_length'
        ),
        sa.CheckConstraint(
            'credential_version >= 0',
            name='credential_version_non_negative'
        )
    )



