from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from app.core.db.base import BaseModel

from app.extensions.datasources.model import DatasourceMixin


class GuacamoleSource(BaseModel, DatasourceMixin):
    __tablename__ = 'guacamole_source'

    endpoint = mapped_column(String, nullable=False)
    datasource = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
