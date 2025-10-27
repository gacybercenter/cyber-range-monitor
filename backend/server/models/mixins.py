import uuid
from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from server.models.base import MappedBase
from server.models.types import mapped_uuid_column


class Record(MappedBase):
    '''
    Represents a database record with a unique identifier,
    should be used to create all subsequent database models.
    '''

    __abstract__ = True

    def __eq__(self, __value: object | Any) -> bool:  # noqa: PYI063
        return isinstance(__value, self.__class__) and self.id == __value.id  # type: ignore

    def __repr__(self) -> str:
        inspected = sa.inspect(self)
        if inspected.identity is not None:
            record_id = inspected.identity[0]
            return f'{self.__class__.__name__}(id={record_id!r})'
        return f'{self.__class__.__name__}(id=None)'


class TimestampedMixin:
    created_at: MappedColumn[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        doc='Timestamp when the record was created',
    )

    updated_at: MappedColumn[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
        doc='Timestamp when the record was last updated',
    )


class Datasource(Record):
    '''
    Polymorphic base class for different types of datasources.
    Contains common fields shared across all datasource types
    and serves as the parent table for specific datasource implementations.
    To learn more about polymorphic mapping in SQLAlchemy, see:
    https://docs.sqlalchemy.org/en/20/orm/inheritance.html#single-table-inheritance

    Columns
    -------
    id : str
        Unique identifier for the datasource (UUID format).
    username : str
        The username for the datasource (not unique).
    password_cipher : str
        Encrypted password for the datasource.
    description : str | None
        Optional description of the datasource.
    connected : bool
        Indicates if the datasource is active, only one datasource
        for a certain category can be enabled at a time.
    label : str
        Human-readable label for the datasource, must be unique.

    Indexes
    -------
    - label
    - connected
    '''

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_uuid_column()

    username: Mapped[str] = mapped_column(
        sa.String(128), nullable=False, doc='Unique name of the datasource'
    )

    password_cipher: Mapped[bytes] = mapped_column(
        sa.BLOB, nullable=False, doc='Encrypted password for the datasource'
    )

    description: Mapped[str | None] = mapped_column(
        sa.String(256), nullable=True, doc='Optional description of the datasource'
    )

    label: Mapped[str] = mapped_column(
        sa.String(128),
        nullable=False,
        unique=True,
        index=True,
        doc='human-readable label for the datasource',
    )

    connected: Mapped[bool] = mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        index=True,
        doc='Indicates if the datasource is active',
    )

    __table_args__ = (
        sa.CheckConstraint('LENGTH(label) >= 3', name='ck_datasource_label_length'),
    )
