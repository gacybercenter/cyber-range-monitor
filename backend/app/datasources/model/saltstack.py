from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .datasource_mixin import DatasourceMixin, Base


class Saltstack(Base, DatasourceMixin):
    __tablename__ = "saltstack"

    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    hostname: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Saltstack(id={self.id}, endpoint="{self.endpoint}", hostname="{self.hostname}")>'
