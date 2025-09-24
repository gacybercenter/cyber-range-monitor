

import uuid
from typing import TypeAlias

import sqlalchemy as sql
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.core.enums import DatasourceCategory
from range_monitor.db.models.mixins import SqlORM
from range_monitor.db.orm_types import GUID


class Datasource(SqlORM):
    '''
    Polymorphic base class for different types of datasources.
    Contains common fields shared across all datasource types
    and serves as the parent table for specific datasource implementations.
    To learn more about polymorphic mapping in SQLAlchemy, see:
    https://docs.sqlalchemy.org/en/20/orm/inheritance.html#single-table-inheritance

    Columns
    -------
    id : str
        Unique identifier for the datasource (UUID format).
    username : str
        The username for the datasource (not unique).
    password_cipher : str
        Encrypted password for the datasource.
    description : str | None
        Optional description of the datasource.
    enabled : bool
        Indicates if the datasource is active, only one datasource
        for a certain category can be enabled at a time.
    category : DatasourceCategory
        Category/type of the datasource (e.g., GUACAMOLE, OPENSTACK, SALTSTACK).
    label : str
        Human-readable label for the datasource, must be unique.

    Indexes
    -------
    - category
    - enabled
    - label


    Triggers
    --------
    - After update of `enabled` field, ensure only one datasource
    per category is enabled. This is enforced at the database level
    '''

    __tablename__ = 'datasources'


    username: Mapped[str] = mapped_column(
        sql.String(128),
        nullable=False,
        unique=True,
        doc='Unique name of the datasource'
    )

    password_cipher: Mapped[str] = mapped_column(
        sql.String(1024),
        nullable=False,
        doc='Encrypted password for the datasource'
    )

    description: Mapped[str | None] = mapped_column(
        sql.String(256),
        nullable=True,
        doc='Optional description of the datasource'
    )

    enabled: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        doc='Indicates if the datasource is active'
    )

    category: Mapped[DatasourceCategory] = mapped_column(
        sql.Enum(DatasourceCategory),
        nullable=False,
        index=True,
        doc='Category/type of the datasource'
    )

    label: Mapped[str] = mapped_column(
        sql.String(128),
        nullable=False,
        unique=True,
        index=True,
        doc='human-readable label for the datasource'
    )


    __mapper_args__ = {
        'polymorphic_on': category,
        'polymorphic_identity': DatasourceCategory.UNKNOWN,
        'with_polymorphic': '*'
    }



class Guacamole(Datasource):
    '''
    Guacamole datasource model inheriting from the base Datasource class.

    Columns
    -------
    id : str
        Foreign primary key to the associated datasource (UUID format).
    hostname : str
        Base URL for the Guacamole API.
    data_source_type : str
        Type of the Guacamole data source (e.g., "mysql", "postgresql").
    '''
    __tablename__ = 'guacamole_datasources'


    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        sql.ForeignKey('datasources.id', ondelete='CASCADE'),
        nullable=False,
        primary_key=True,
        doc='Foreign key to the associated datasource'
    )


    hostname: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='Base URL for the Guacamole API'
    )

    data_source_type: Mapped[str] = mapped_column(
        sql.String(32),
        nullable=False,
        doc='Type of the Guacamole data source (e.g., "mysql", "postgresql")'
    )

    __mapper_args__ = {
        'polymorphic_identity': DatasourceCategory.GUACAMOLE,
    }

class OpenStack(Datasource):
    '''
    OpenStack datasource model inheriting from the base Datasource class.

    Columns
    -------
    id : str
        Foreign primary key to the associated datasource (UUID format).
    auth_url : str
        Authentication URL for the OpenStack API.
    user_domain_name : str
        User domain name for OpenStack authentication.
    region_name : str
        Region name for the OpenStack services.
    identity_api_version : str
        Version of the OpenStack Identity API (e.g., "v3").
    project_id : str | None
        Optional project ID for scoping OpenStack operations.
    project_name : str | None
        Optional project name for scoping OpenStack operations.
    project_domain_name : str | None
        Optional project domain name for OpenStack authentication.

    Constraints
    -----------
    - If `project_id` is provided, `project_name` and `project_domain_name` must be null
    '''
    __tablename__ = 'openstack_datasources'


    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        sql.ForeignKey('datasources.id', ondelete='CASCADE'),
        primary_key=True,
        doc='Foreign key to the associated datasource'
    )

    auth_url: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='Authentication URL for the OpenStack API'
    )

    user_domain_name: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='User domain name for OpenStack authentication'
    )

    region_name: Mapped[str] = mapped_column(
        sql.String(64),
        nullable=False,
        doc='Region name for the OpenStack services'
    )

    identity_api_version: Mapped[str] = mapped_column(
        sql.String(8),
        nullable=False,
        doc='Version of the OpenStack Identity API (e.g., "v3")'
    )

    project_id: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project ID for scoping OpenStack operations'
    )

    project_name: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project name for scoping OpenStack operations'
    )

    project_domain_name: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project domain name for OpenStack authentication'
    )

    __mapper_args__ = {
        'polymorphic_identity': DatasourceCategory.OPENSTACK,
    }




class SaltStack(Datasource):
    '''
    SaltStack datasource model inheriting from the base Datasource class.

    Columns
    -------
    id : str
        Foreign primary key to the associated datasource (UUID format).
    endpoint : str
        Base URL for the SaltStack API.
    hostname : str
        Hostname for the SaltStack server.

    '''
    __tablename__ = 'saltstack_datasources'


    id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        sql.ForeignKey('datasources.id', ondelete='CASCADE'),
        primary_key=True,
        doc='Foreign key to the associated datasource'
    )


    endpoint: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='Base URL for the SaltStack API'
    )

    hostname: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='Hostname for the SaltStack server'
    )

    __mapper_args__ = {
        'polymorphic_identity': DatasourceCategory.SALTSTACK,
    }

DataSourceTypes: TypeAlias = Guacamole | OpenStack | SaltStack