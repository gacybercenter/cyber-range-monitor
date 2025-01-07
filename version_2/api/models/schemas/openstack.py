from pydantic import BaseModel, Field, ConfigDict, HttpUrl, model_validator
from api.models.schemas.shared import (
    SchemaCheck,
    DatasourceCreateBase,
    DatasourceUpdateBase,
    DatasourceReadBase,
)
from typing import Optional


class OpenstackRead(DatasourceReadBase):
    auth_url: str
    project_id: Optional[str]
    project_name: Optional[str]
    user_domain_name: str
    project_domain_name: Optional[str]
    region_name: str
    identity_api_version: str
    
    model_config = ConfigDict(from_attributes=True)
    

class OpenstackCreate(DatasourceCreateBase):
    auth_url: HttpUrl = Field(...) 
    project_id: Optional[str] = Field(None, min_length=1, max_length=255)

    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    
    user_domain_name: str = Field(..., min_length=1, max_length=255)
    
    project_domain_name: Optional[str] = Field(..., min_length=1, max_length=255)
    region_name: str = Field(..., min_length=1, max_length=255)  

    identity_api_version: str = Field(..., min_length=1, max_length=2)

    
    @model_validator(mode='after')
    def check_model(cls, v):
        SchemaCheck.check_api_version(v.identity_api_version)
        return v

class OpenstackUpdate(DatasourceUpdateBase):
    auth_url: Optional[HttpUrl] = Field(None) 

    project_id: Optional[str] = Field(None, min_length=1, max_length=255)
    project_name: Optional[str] = Field(None, min_length=1, max_length=255)
    region_name: Optional[str] = Field(None, min_length=1, max_length=255)  

    user_domain_name: Optional[str] = Field(None, min_length=1, max_length=255)
    project_domain_name: Optional[str] = Field(None, min_length=1, max_length=255)

    identity_api_version: Optional[str] = Field(None, min_length=1, max_length=2)
    
    @model_validator(mode='after')
    def check_model(cls, v):
        if v.identity_api_version:
            SchemaCheck.check_api_version(v.identity_api_version)
        return v


    