
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.api.domains.datasource.models import DataSource
from app.infrastructure import db
from app.infrastructure.model_mixins import AuditedMixin


class GuacamoleDataSource(DataSource, AuditedMixin, db.Base):
    __tablename__ = 'guac_datasources'


    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
