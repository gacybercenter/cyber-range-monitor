from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import Base, DatasourceMixin


class SaltstackSource(Base, DatasourceMixin):
    __tablename__ = "saltstack_datasources"

    hostname: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Saltstack(id={self.id}, endpoint="{self.endpoint}", hostname="{self.hostname}")>'
