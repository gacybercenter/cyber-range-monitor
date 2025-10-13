from datetime import UTC, datetime
from typing import Final

import sqlalchemy as sql
from sqlalchemy.orm import DeclarativeBase, MappedColumn, mapped_column


class MappedModel(DeclarativeBase):
    __abstract__ = True

    metadata = sql.MetaData(
        naming_convention={
            'ix': 'ix_%(table_name)s_%(column_0_name)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        }
    )


SQLITE_UTC_FUNC: Final[str] = "datetime('now', 'utc')"


def UTCDatetime() -> MappedColumn[sql.DateTime]:
    return mapped_column(
        sql.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=SQLITE_UTC_FUNC,
        doc='Timestamp in UTC',
    )


class SqlModel(MappedModel):
    """
    Represents a database record with a unique identifier,
    should be used to create all subsequent database models.
    """

    __abstract__ = True

    def __eq__(self, __value: object) -> bool:
        # type: ignore
        return isinstance(__value, self.__class__) and self.id == __value.id  # type: ignore

    def __repr__(self) -> str:
        inspected = sql.inspect(self)
        if inspected.identity is not None:
            record_id = inspected.identity[0]
            return f'{self.__class__.__name__}(id={record_id!r})'
        return f'{self.__class__.__name__}(id=None)'
