
from pydantic import BaseModel, Field, ConfigDict
from api.models.schemas.shared import (
    DatasourceCreateBase,
    DatasourceUpdateBase,
    DatasourceReadBase,
)
from typing import Optional

class SaltstackRead(DatasourceReadBase):
    endpoint: str
    hostname: str
    
    model_config = ConfigDict(from_attributes=True)

    
class SaltstackCreate(DatasourceCreateBase):
    endpoint: str = Field(..., min_length=1, max_length=255)
    hostname: str = Field(..., min_length=1, max_length=255)
    
class SaltstackUpdate(DatasourceUpdateBase):
    endpoint: Optional[str] = Field(None, min_length=1, max_length=255)
    hostname: Optional[str] = Field(None, min_length=1, max_length=255)
    






