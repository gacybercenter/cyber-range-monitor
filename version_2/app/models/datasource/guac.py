from sqlalchemy import String
from sqlalchemy.orm import mapped_column
from app.models.base import Base
from app.models.mixins import DatasourceMixin

class Guacamole(Base, DatasourceMixin):
    __tablename__ = 'guacamole'

    endpoint = mapped_column(String, nullable=False)
    datasource = mapped_column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
    