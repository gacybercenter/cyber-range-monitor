
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.datasource.models import DataSource
from range_monitor.model import RecordModel


class SaltStackDataSource(DataSource, RecordModel):
    __tablename__ = 'datasource_saltstack'

    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )