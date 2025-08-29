import uuid
from datetime import UTC, datetime

from sqlalchemy import MetaData, String, inspect
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

db_meta = MetaData(
    naming_convention={
        'ix': 'ix_%(column_0_N_label)s',
        'uq': '%(table_name)s_%(column_0_N_name)s_key',
        'ck': '%(table_name)s_%(constraint_name)s_check',
        'fk': '%(table_name)s_%(column_0_N_name)s_fkey',
        'pk': '%(table_name)s_pkey',
    }
)


class MappedModel(DeclarativeBase, AsyncAttrs):
    __abstract__ = True

    metadata = db_meta


class TimestampedMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )



class RecordModel(MappedModel):
    """
    Represents a database record with a unique identifier,
    should be used to create all subsequent database models.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, self.__class__) and self.id == __value.id

    def __hash__(self) -> int:
        return self.id.int

    def __repr__(self) -> str:
        inspected = inspect(self)
        if inspected.identity is not None:
            record_id = inspected.identity[0]
            return f'{self.__class__.__name__}(id={record_id!r})'
        return f'{self.__class__.__name__}(id=None)'

