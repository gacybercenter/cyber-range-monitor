from sqlalchemy import Column, Integer, String, Boolean


class DatasourceMixin(object):
    '''The shared columns for all of the Datasource models'''
    id = Column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )

    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    enabled = Column(Boolean, default=False)
