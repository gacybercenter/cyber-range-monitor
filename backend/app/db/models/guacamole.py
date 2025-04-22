from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from .base import DatabaseModel

from app.core.mixins.datasource import DatasourceMixin


class GuacamoleSource(DatabaseModel, DatasourceMixin):
    __tablename__ = 'guacamole_source'

    datasource = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
