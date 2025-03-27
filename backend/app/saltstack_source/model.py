from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import BaseModel

from app.extensions.datasources.model import DatasourceMixin


class SaltstackSource(BaseModel, DatasourceMixin):
    __tablename__ = 'saltstack_source'
    
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    hostname: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Saltstack(id={self.id}, endpoint="{self.endpoint}", hostname="{self.hostname}")>'
