from sqlalchemy import  Integer, String, Boolean
from sqlalchemy.orm import mapped_column, Mapped
from app.core.security import crypto_utils



class DatasourceMixin(object):
    '''The shared mapped_columns for all of the Datasource models'''
    id = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(String, nullable=False)
    encrypted_password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)

    @property
    def password(self) -> str:
        return crypto_utils.decrypt_data(self.encrypted_password)
    
    def __init__(self, **kwargs) -> None:
        if kwargs.get('password'):
            kwargs['encrypted_password'] = crypto_utils.encrypt_data(kwargs['password'])
            del kwargs['password']
        super().__init__(**kwargs)
        
        
    
    
    
    
    
    
    
    
    
    