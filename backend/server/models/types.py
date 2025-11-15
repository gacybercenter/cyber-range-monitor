from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

import sqlalchemy as sa
from sqlalchemy.orm import MappedColumn, mapped_column

if TYPE_CHECKING:
    from sqlalchemy.types import TypeEngine


class UUIDLite(sa.TypeDecorator):
    """
    An implementation of UUIDs in SQLAlchemy for SQLite
    """

    cache_ok = True
    impl = sa.BLOB

    def load_dialect_impl(self, dialect: sa.Dialect) -> TypeEngine[bytes]:
        return dialect.type_descriptor(sa.BLOB(16))

    def process_bind_param(self, value: Any, dialect: sa.Dialect) -> bytes | None:
        if value is None:
            return value

        if isinstance(value, str):
            value = uuid.UUID(value)

        if not isinstance(value, uuid.UUID):
            raise TypeError('value must be a uuid.UUID or string')

        return value.bytes

    def process_result_value(self, value: Any, dialect: sa.Dialect) -> uuid.UUID | None:
        if value is None:
            return value
        return uuid.UUID(bytes=bytes(value))

    @classmethod
    def default(cls) -> uuid.UUID:
        return uuid.uuid4()


def mapped_uuid_column(**kwargs: Any) -> MappedColumn[uuid.UUID]:
    """
    Helper function to create a mapped UUID column with default settings.
    """
    return mapped_column(
        UUIDLite,
        primary_key=kwargs.pop('primary_key', True),
        default=kwargs.pop('default', UUIDLite.default),
        nullable=kwargs.pop('nullable', False),
        **kwargs,
    )
