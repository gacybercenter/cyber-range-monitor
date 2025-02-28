from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class DatasourceMixin(object):
    '''The shared mapped_columns for all of the Datasource models'''
    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    
        
    
    
    
    
    
    
    
    
    
    