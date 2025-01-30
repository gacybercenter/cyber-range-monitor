from sqlalchemy import Column, String

 app.models.base import Base
from app.models.mixins import DatasourceMixin

class Guacamole(Base, DatasourceMixin):
    __tablename__ = 'guacamole'

    endpoint = Column(String, nullable=False)
    datasource = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Guacamole(id={self.id}, endpoint="{self.endpoint}", datasource="{self.datasource}")>'
    