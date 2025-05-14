from datetime import datetime, UTC
from typing import Annotated
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs


class MappedBase(AsyncAttrs, DeclarativeBase):
    '''base model all database models must inherit from'''


PKId = Annotated[int, mapped_column(
    autoincrement=True,
    primary_key=True,
    index=True,
    unique=True
)]


class AuditedMixin:

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )


class DatasourceMixin:

    id: Mapped[PKId] = mapped_column()

    username: Mapped[str] = mapped_column(String, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )


class Base(MappedBase):
    '''base model all database models must inherit from'''
    __abstract__ = True
