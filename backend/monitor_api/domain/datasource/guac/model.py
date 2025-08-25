
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from monitor_api.domain.domains.datasource.models import DataSource
from monitor_api.infrastructure import db
from monitor_api.infrastructure.model_mixins import AuditedMixin


class GuacamoleDataSource(DataSource, AuditedMixin, db.Base):
    __tablename__ = 'guac_datasources'


    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
