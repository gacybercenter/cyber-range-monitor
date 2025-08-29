
from datetime import UTC, datetime

from sqlalchemy import Enum, String, case
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.model import RecordModel, TimestampedMixin

from .roles import RoleLevels, UserRoles


class User(RecordModel, TimestampedMixin):
    """Represents a user in the database"""

    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )

    role: Mapped[UserRoles] = mapped_column(
        Enum(UserRoles),
        default=UserRoles.USER,
        nullable=False
    )

    @hybrid_property
    def role_level(self) -> int:
        return RoleLevels.get_level(self.role)

    @role_level.expression
    def role_level(cls):
        return case(
            RoleLevels.LEVELS,
            value=cls.role,
            else_=0
        )


