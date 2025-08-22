
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.api.domains.datasource.models import DataSource
from app.infrastructure import db


class SaltStackDataSource(DataSource, db.Base):
    __tablename__ = 'datasource_saltstack'

    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )