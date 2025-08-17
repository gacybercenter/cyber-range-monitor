from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db_model import Base
from app.infrastructure.model_mixins import AuditedMixin, PrimaryUUIDKey


class DataSourceType(StrEnum):
    GUACAMOLE = 'guacamole'
    OPENSTACK = 'openstack'
    SALTSTACK = 'saltstack'


class DataSource(Base, AuditedMixin):
    __tablename__ = 'datasource'

    id: Mapped[PrimaryUUIDKey] = mapped_column()

    source_type: Mapped[DataSourceType] = mapped_column(
        Enum(DataSourceType),
        nullable=False,
        index=True,
        description='The type of the data source used for polymorphic queries.',
    )

    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        description='The username for the datasource',
    )

    password: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        description='The password for the datasource',
    )

    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        description='The endpoint for the datasource',
    )

    enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
        description='Whether the datasource is enabled or not',
    )

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': None,
        'with_polymorphic': '*',
    }

    __table_args__ = (
        UniqueConstraint(
            'endpoint', 'username', name='uq_datasource_endpoint_username'
        ),
        Index('ix_datasource_enabled_type', 'enabled', 'type'),
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
        description='The type of the guacamole datasource (e.g., "mysql", "postgresql")',
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
        description='The user domain name for OpenStack authentication',
    )

    region_name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        description='The region name for OpenStack services',
    )

    identity_api_version: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        description='The OpenStack identity API version (e.g., "3")',
    )

    # --optional fields--
    project_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        description='The project ID for OpenStack authentication (optional)',
    )

    project_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        description='The project name for OpenStack authentication (optional)',
    )

    project_domain_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        description='The project domain name for OpenStack authentication (optional)',
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
