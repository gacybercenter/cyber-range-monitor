from sqlalchemy import Column, String

from app.models.base import Base
from app.models.mixins import DatasourceMixin


class Saltstack(Base, DatasourceMixin):
    __tablename__ = 'saltstack'

    endpoint = Column(String, nullable=False)
    hostname = Column(String, nullable=False)

    def __repr__(self) -> str:
        return f'<Saltstack(id={self.id}, endpoint="{self.endpoint}", hostname="{self.hostname}")>'
