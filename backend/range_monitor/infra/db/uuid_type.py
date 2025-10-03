import uuid

from sqlalchemy import BLOB, Dialect
from sqlalchemy.orm import MappedColumn, mapped_column
from sqlalchemy.types import CHAR, TypeDecorator


class UUIDLite(TypeDecorator):
    '''
    An implementation of UUIDs for SQLAlchemy
    '''
    cache_ok = True
    impl = CHAR

    def load_dialect_impl(self, dialect: Dialect):
        return dialect.type_descriptor(BLOB(16))


    def process_bind_param(self, value, dialect: Dialect):
        if value is None:
            return value

        if isinstance(value, str):
            value = uuid.UUID(value)

        if not isinstance(value, uuid.UUID):
            raise ValueError('value must be a uuid.UUID or string')

        return value.bytes

    def process_result_value(self, value, dialect: Dialect):
        if value is None:
            return value
        return uuid.UUID(bytes=bytes(value))

    @classmethod
    def default(cls):
        return uuid.uuid4()


def PrimaryKeyUUID() -> MappedColumn[uuid.UUID]:
    '''
    A convenience function to create a primary key UUID column.
    '''
    return mapped_column(
        UUIDLite,
        primary_key=True,
        default=UUIDLite.default,
        unique=True,
        nullable=False,
        index=True,
        doc='Primary key UUID'
    )