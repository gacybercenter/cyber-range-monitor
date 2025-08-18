from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db import Base
from app.infrastructure.model_mixins import AuditedMixin, PrimaryUUIDKey


class DataSourceType(StrEnum):
    GUACAMOLE = 'guacamole'
    OPENSTACK = 'openstack'
    SALTSTACK = 'saltstack'


class DataSource(Base, AuditedMixin):
    __tablename__ = 'datasources'

    id: Mapped[PrimaryUUIDKey] = mapped_column()

    source_type: Mapped[DataSourceType] = mapped_column(
        Enum(DataSourceType),
        nullable=False,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    __mapper_args__ = {
        'polymorphic_on': source_type,
        'with_polymorphic': '*',
    }

    __table_args__ = (
        UniqueConstraint(
            'endpoint', 'username', name='uq_datasource_endpoint_username'
        ),
        Index('ix_datasource_enabled_type', 'enabled', 'source_type'),
    )


class GuacamoleDataSource(DataSource):
    __tablename__ = 'datasource_guacamole'

    id: Mapped[PrimaryUUIDKey] = mapped_column(
        ForeignKey('datasources.id', ondelete='CASCADE'),
        primary_key=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.GUACAMOLE,
    }


class OpenStackDataSource(DataSource):
    __tablename__ = 'datasource_openstack'

    id: Mapped[PrimaryUUIDKey] = mapped_column(
        ForeignKey('datasources.id', ondelete='CASCADE'),
        primary_key=True,
        index=True,
    )
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

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.OPENSTACK,
    }


class SaltStackDataSource(DataSource):
    __tablename__ = 'datasource_saltstack'

    id: Mapped[PrimaryUUIDKey] = mapped_column(
        ForeignKey('datasources.id', ondelete='CASCADE'),
        primary_key=True,
        index=True,
    )
    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.SALTSTACK,
    }
