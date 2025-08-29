

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.domain.domains.datasource.models import DataSource
from range_monitor.infrastructure import db
from range_monitor.infrastructure.model_mixins import AuditedMixin, PrimaryUUIDKey


class OpenStackDataSource(DataSource, AuditedMixin, db.Base):
    __tablename__ = 'datasource_openstack'

    id: Mapped[PrimaryUUIDKey] = mapped_column()

    # --required fields--
    user_domain_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    region_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    identity_api_version: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    # --optional fields--
    project_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    project_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    project_domain_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )