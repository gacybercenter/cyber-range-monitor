from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    '''base model; all ORM models MUST inherit from this class'''
    pass
