# app/domain/auth/models.py
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.model import RecordModel


class User(RecordModel):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    role_id: Mapped[int | None] = mapped_column(
        ForeignKey('roles.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    role: Mapped['Role'] = relationship('Role', back_populates='users')


class Role(RecordModel):
    __tablename__ = 'roles'

    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    users: Mapped[list['User']] = relationship('User', back_populates='role')
    scopes_json: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )