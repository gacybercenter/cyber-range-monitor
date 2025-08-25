
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from monitor_api.domain.domains.datasource.models import DataSource
from monitor_api.infrastructure import db


class SaltStackDataSource(DataSource, db.Base):
    __tablename__ = 'datasource_saltstack'

    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )