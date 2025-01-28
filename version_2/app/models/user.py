from sqlalchemy import Column, Integer, String, CheckConstraint
from enum import Enum

from app.models.base import Base
from app.models.mixins import AuditedMixin


class UserRoles(str, Enum):
    admin = 'admin'
    user = 'user'
    read_only = 'read_only'

    def __ge__(self, other: 'UserRoles | str') -> bool:
        if isinstance(other, str): 
            other = UserRoles(other)

        hierarchy = {
            UserRoles.admin: 3,
            UserRoles.user: 2,
            UserRoles.read_only: 1
        }
        return hierarchy[self] >= hierarchy[other]


class User(Base, AuditedMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, default=UserRoles.user)
    password_hash = Column(String, nullable=False)

    __table_args__ = (
        CheckConstraint(
            role.in_([perm.value for perm in UserRoles]),
            name="is_valid_permission"
        ),
    )

    def __repr__(self) -> str:
        return f'<User(id={self.id} username={self.username} role={self.role})>'
