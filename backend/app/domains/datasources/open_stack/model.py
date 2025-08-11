from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from domains.model_mixins import DatasourceMixin, Base


class OpenstackSource(Base, DatasourceMixin):
    __tablename__ = "openstack_datasources"

    user_domain_name: Mapped[str] = mapped_column(String, nullable=False)
    region_name: Mapped[str] = mapped_column(String, nullable=False)
    identity_api_version: Mapped[str] = mapped_column(String, nullable=False)

    project_id: Mapped[str | None] = mapped_column(String, nullable=True)
    project_name: Mapped[str | None] = mapped_column(String, nullable=True)
    project_domain_name: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self) -> str:
        return f'<Openstack(id={self.id}, auth_url="{self.endpoint}", region="{self.region_name}", project="{self.project_name or "None"}")>'
