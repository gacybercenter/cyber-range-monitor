import sqlalchemy as sql
from sqlalchemy.orm import Mapped, mapped_column

from server.models.mixins import Datasource, Record


class Guacamole(Datasource, Record):
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

    hostname: Mapped[str] = mapped_column(
        sql.String(256), nullable=False, doc='Base URL for the Guacamole API'
    )

    data_source_type: Mapped[str] = mapped_column(
        sql.String(32),
        nullable=False,
        doc='Type of the Guacamole data source (e.g., "mysql", "postgresql")',
    )


class Openstack(Datasource, Record):
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

    auth_url: Mapped[str] = mapped_column(
        sql.String(256), nullable=False, doc='Authentication URL for the OpenStack API'
    )

    user_domain_name: Mapped[str] = mapped_column(
        sql.String(256),
        nullable=False,
        doc='User domain name for OpenStack authentication',
    )

    region_name: Mapped[str] = mapped_column(
        sql.String(64), nullable=False, doc='Region name for the OpenStack services'
    )

    identity_api_version: Mapped[str] = mapped_column(
        sql.String(8),
        nullable=False,
        doc='Version of the OpenStack Identity API (e.g., "v3")',
    )

    project_id: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project ID for scoping OpenStack operations',
    )

    project_name: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project name for scoping OpenStack operations',
    )

    project_domain_name: Mapped[str | None] = mapped_column(
        sql.String(64),
        nullable=True,
        doc='Optional project domain name for OpenStack authentication',
    )


class Saltstack(Datasource, Record):
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

    endpoint: Mapped[str] = mapped_column(
        sql.String(256), nullable=False, doc='Base URL for the SaltStack API'
    )

    hostname: Mapped[str] = mapped_column(
        sql.String(256), nullable=False, doc='Hostname for the SaltStack server'
    )


type DatasourceORM = Guacamole | Openstack | Saltstack
