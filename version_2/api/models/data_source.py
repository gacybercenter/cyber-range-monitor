
from api.db.main import Base
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime, timezone
from api.models.mixins import DatasourceMixin


class Guacamole(Base, DatasourceMixin):
    __tablename__ = 'guacamole'

    endpoint = Column(String, nullable=False)
    datasource = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<GUACAMOLE_{self.id}: {self.endpoint}>'


class Openstack(Base, DatasourceMixin):
    __tablename__ = 'openstack'

    auth_url = Column(String, nullable=False)
    user_domain_name = Column(String, nullable=False)
    region_name = Column(String, nullable=False)
    identity_api_version = Column(String, nullable=False)
    
    project_id = Column(String)
    project_name = Column(String)
    project_domain_name = Column(String)

    def __repr__(self) -> str:
        return f'<OPENSTACK_{self.id}: {self.auth_url}>'


class Saltstack(Base, DatasourceMixin):
    __tablename__ = 'saltstack'

    endpoint = Column(String, nullable=False)
    hostname = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<SALTSTACK_{self.id}: {self.endpoint}>'
