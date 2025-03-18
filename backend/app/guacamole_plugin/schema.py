import json
import time
from app.core.schemas import CustomBaseModel
from pydantic import Field

from guacamole_source.schema import GuacamoleProtectedRead, GuacamoleRead




class GuacConnectionSource(CustomBaseModel):
    host: str
    username: str
    password: str
    data_source: str
    





    
    
class CachedGuacConnection(CustomBaseModel):
    source: GuacConnectionSource
    last_connected: float = Field(
        ...,
        description='the time since last connected'
    )
    
    @classmethod
    def from_schema(cls, guac_read: GuacamoleProtectedRead) -> 'CachedGuacConnection':
        return cls(
            source=GuacConnectionSource(
                host=guac_read.endpoint,
                username=guac_read.username,
                password=guac_read.password,
                data_source=guac_read.datasource
            ),
            last_connected=time.time()
        )
    
    @classmethod
    def loads(cls, json_str: str) -> 'CachedGuacConnection':
        schema = json.loads(json_str)
        return cls(**schema)
        
        

        
    
        
        
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        




