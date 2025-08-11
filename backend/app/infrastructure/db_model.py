
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class MappedBase(AsyncAttrs, DeclarativeBase):
    pass

class Base(MappedBase):
    __abstract__ = True

