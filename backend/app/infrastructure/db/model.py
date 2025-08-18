from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class MappedBase(AsyncAttrs, DeclarativeBase):
    pass


class Base(MappedBase):
    '''
    Base class for all ORMs
    '''
    __abstract__ = True
