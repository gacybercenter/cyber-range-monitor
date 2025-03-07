from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from .datasource_mixin import DatasourceMixin, Base


class Guacamole(Base, DatasourceMixin):
    __tablename__ = "guacamole"

    endpoint = mapped_column(String, nullable=False)
    datasource = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
