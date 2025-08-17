from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from domains.model_mixins import DatasourceMixin, Base


class GuacamoleSource(Base, DatasourceMixin):
    __tablename__ = 'guacamole_datasources'

    datasource = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
