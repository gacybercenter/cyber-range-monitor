from pydantic import BaseModel, Field, ConfigDict
from api.models.schemas.shared import (
    SchemaCheck,
    DatasourceCreateBase,
    DatasourceUpdateBase,
    DatasourceReadBase,
)
from typing import Optional

class GuacRead(DatasourceReadBase):
    datasource: str
    endpoint: str
    
    model_config = ConfigDict(from_attributes=True)

class GuacCreate(DatasourceCreateBase):
    datasource: str = Field(..., min_length=1, max_length=255)
    endpoint: str = Field(..., min_length=1, max_length=255)
    
class GuacUpdate(DatasourceUpdateBase):
    datasource: Optional[str] = Field(None, min_length=1, max_length=255)
    endpoint: Optional[str] = Field(None, min_length=1, max_length=255)