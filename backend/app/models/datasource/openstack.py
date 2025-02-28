
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

from .datasource_mixin import DatasourceMixin


class Openstack(Base, DatasourceMixin):
    __tablename__ = 'openstack'

    auth_url: Mapped[str] = mapped_column(String, nullable=False)
    user_domain_name: Mapped[str] = mapped_column(String, nullable=False)
    region_name: Mapped[str] = mapped_column(String, nullable=False)
    identity_api_version: Mapped[str] = mapped_column(String, nullable=False)

    project_id: Mapped[Optional[str]] = mapped_column(String)
    project_name: Mapped[Optional[str]] = mapped_column(String)
    project_domain_name: Mapped[Optional[str]] = mapped_column(String)

    def __repr__(self) -> str:
        return f'<Openstack(id={self.id}, auth_url="{self.auth_url}", region="{self.region_name}", project="{self.project_name or "None"}")>'
