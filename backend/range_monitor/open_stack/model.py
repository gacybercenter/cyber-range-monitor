from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.datasource.model import DataSource, DataSourceType


class OpenStack(DataSource):
    __tablename__ = 'datasource_openstack'

    id: Mapped[str] = mapped_column(
        ForeignKey('datasource.id', ondelete='CASCADE'), primary_key=True
    )
    auth_url: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    user_domain_name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )
    region_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    identity_api_version: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
    )

    project_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    project_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    project_domain_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.OPENSTACK,
    }
