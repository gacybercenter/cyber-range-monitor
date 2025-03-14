from sqlalchemy.orm import DeclarativeBase
from .options import DatabaseEngineOptions

ENGINE_OPTIONS = DatabaseEngineOptions()

class Base(DeclarativeBase):
    pass


