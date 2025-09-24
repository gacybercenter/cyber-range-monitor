

import uuid
from sqlalchemy import BLOB, Dialect, ForeignKey
from sqlalchemy.orm import MappedColumn, mapped_column
from sqlalchemy.types import CHAR, TypeDecorator


class GUID(TypeDecorator):
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


def MappedPrimaryKeyID(
    doc: str = 'Unique identifier for the record',
    foreign_key: ForeignKey | None = None,
) -> MappedColumn[uuid.UUID]:
    args = []
    if foreign_key is not None:
        args.append(foreign_key)

    return mapped_column(
        GUID(),
        *args,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        doc=doc
    )

