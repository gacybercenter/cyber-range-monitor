from api.db.main import Base
from sqlalchemy import Column, Integer, DateTime, String, CheckConstraint
from datetime import datetime, timezone
from api.models.mixins import AuditedMixin
from enum import Enum


class UserRoles(str, Enum):
    admin = 'admin'
    user = 'user'
    read_only = 'read_only'


class User(Base, AuditedMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    permission = Column(String, default=UserRoles.user)
    password_hash = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(
            permission.in_([perm.value for perm in UserRoles]),
            name="is_valid_permission"
        ),
    )

    def __repr__(self) -> str:
        return f'<USER_{self.id}: {self.username}>'
