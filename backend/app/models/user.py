from sqlalchemy import Case, Enum, Integer, String, case
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from .audited_mixin import AuditedMixin
from .enums import Role


class User(Base, AuditedMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        index=True
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True
    )
    role: Mapped[Role] = mapped_column(
        Enum(Role),
        default=Role.USER,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    
    @hybrid_property
    def role_level(self) -> int:  # type: ignore
        return Role.get_role_level(self.role)

    @role_level.expression
    def role_level(cls) -> Case:
        return case(
            (cls.role == Role.READ_ONLY, 1), # type: ignore
            (cls.role == Role.USER, 2), # type: ignore
            (cls.role == Role.ADMIN, 3), # type: ignore
            else_=-1
        )

    def is_authorized(self, required_role: Role) -> bool:
        return self.role >= required_role

    def __repr__(self) -> str:
        return f'<User(id={self.id} username={self.username} role={self.role})>'
