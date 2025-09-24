from enum import StrEnum

from sqlalchemy import Boolean, LargeBinary, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.db.base import RecordModel, TimestampedMixin


class DatasourceType(StrEnum):
    GUACAMOLE = 'guacamole'
    OPENSTACK = 'openstack'
    SALTSTACK = 'saltstack'


class Datasource(TimestampedMixin):
    '''
    The shared columns for all datasource types and has
    an associative one-to-one relationship with each specific
    datasource type table as opposed to polymorphic inheritance.

    This is to avoid the complexity of polymorphic queries and so
    you don't need to be an SQLAlchemy expert to understand this.
    '''
    __abstract__ = True


    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )

    password_ciphertext: Mapped[bytes] = mapped_column(
        LargeBinary(length=8192),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True
    )



class Guacamole(Datasource, RecordModel):
    __tablename__ = 'guacamole'


    host: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    data_source: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
    )

class OpenStack(Datasource, RecordModel):
    __tablename__ = 'openstack'


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


class SaltStack(Datasource, RecordModel):
    __tablename__ = 'saltstack'


    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )