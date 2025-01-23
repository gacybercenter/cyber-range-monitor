
from api.models.base import Base
from sqlalchemy import Column, String
from api.models.mixins import DatasourceMixin


class Guacamole(Base, DatasourceMixin):
    __tablename__ = 'guacamole'

    endpoint = Column(String, nullable=False)
    datasource = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'


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
        return f'<Openstack(id={self.id}, auth_url="{self.auth_url}", region="{self.region_name}", project="{self.project_name or "None"}")>' 


class Saltstack(Base, DatasourceMixin):
    __tablename__ = 'saltstack'

    endpoint = Column(String, nullable=False)
    hostname = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Saltstack(id={self.id}, endpoint="{self.endpoint}", hostname="{self.hostname}")>'
