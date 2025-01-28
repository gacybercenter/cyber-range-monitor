
from sqlalchemy import Column, String

from app.models.base import Base
from app.models.mixins import DatasourceMixin



class Openstack(Base, DatasourceMixin):
    __tablename__ = 'openstack'

    auth_url = Column(String, nullable=False)
    user_domain_name = Column(String, nullable=False)
    region_name = Column(String, nullable=False)
    identity_app_version = Column(String, nullable=False)

    project_id = Column(String)
    project_name = Column(String)
    project_domain_name = Column(String)

    def __repr__(self) -> str:
        return f'<Openstack(id={self.id}, auth_url="{self.auth_url}", region="{self.region_name}", project="{self.project_name or "None"}")>'

