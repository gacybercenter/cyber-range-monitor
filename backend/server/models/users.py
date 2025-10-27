import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from server.enums import RoleLevelMap, UserRoles
from server.models.mixins import Record, TimestampedMixin, mapped_uuid_column


class User(Record, TimestampedMixin):
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
    Triggers
    --------
    - Before update of `role` or `password_hash`, increment `credential_version`
    enforced at the database level.
    '''

    id: Mapped[uuid.UUID] = mapped_uuid_column()

    username: Mapped[str] = mapped_column(
        sa.String(128),
        nullable=False,
        unique=True,
        index=True,
        doc='Unique username for the user, indexed',
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
        doc='Role assigned to the user, comparable using the hybrid property.',
    )

    credential_version: Mapped[int] = mapped_column(
        default=0,
        nullable=False,
        doc='Version of the user credentials, incremented on password or role change.',
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
        doc='Timestamp of the last login, nullable if never logged in.'
    )

    created_by: Mapped[str] = mapped_column(
        sa.String(128),
        nullable=False,
        doc='Name of the actor who created this user.'
    )

    @hybrid_property
    def role_level(self) -> int:  # type: ignore[override]
        return self.role.level

    @role_level.expression  # pyright: ignore[reportArgumentType]
    def role_level(self):  # noqa: ANN201
        return sa.case(RoleLevelMap, value=self.role, else_=0)

    __table_args__ = (
        sa.CheckConstraint(
            'length(username) >= 3',
            name='username_min_length'
        ),
        sa.CheckConstraint(
            'credential_version >= 0',
            name='credential_version_non_negative'
        ),
    )


