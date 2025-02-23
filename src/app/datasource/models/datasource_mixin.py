from sqlalchemy import  Integer, String, Boolean
from sqlalchemy.orm import mapped_column, Mapped




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

    
        
    
    
    
    
    
    
    
    
    
    