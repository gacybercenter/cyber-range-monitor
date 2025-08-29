

from sqlalchemy import Boolean, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.datasource.types import DataSourceType
from range_monitor.model import RecordModel, TimestampedMixin


class DataSource(RecordModel, TimestampedMixin):
    __tablename__ = 'datasource'


    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    type: Mapped[DataSourceType] = mapped_column(
        SQLEnum(DataSourceType),
        nullable=False,
        index=True
    )
    password_ciphertext: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'datasource',
    }


