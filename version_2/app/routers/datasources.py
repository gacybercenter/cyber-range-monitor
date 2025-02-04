from fastapi import APIRouter
from app.models import Guacamole, Openstack, Saltstack
from app.schemas import (
    GuacCreate, GuacRead, GuacUpdate,
    OpenstackCreate, OpenstackRead, OpenstackUpdate,
    SaltstackCreate, SaltstackRead, SaltstackUpdate
)
from app.services.utils.datasource_factory import DatasourceRouterSchema


def initialize_routers() -> APIRouter:
    '''
    Creates the API Router for all of the Datasources
    using DATASOURCE_SCHEMAS to define the response, body 
    for requests and the associated ORM for the  
    'create_data_source_router' factory function 

    This allows all of the datasources to share the same 
    prefix and handle the responses  

    Returns:
        APIRouter -- the datasource API router
    '''
    ds_router = APIRouter(
        prefix='/datasources'
    )
    DATASOURCE_SCHEMAS = {
        'guac': DatasourceRouterSchema(
            datasource_model=Guacamole,
            create_schema=GuacCreate,
            read_schema=GuacRead,
            update_schema=GuacUpdate
        ),
        'openstack': DatasourceRouterSchema(
            datasource_model=Openstack,
            create_schema=OpenstackCreate,
            read_schema=OpenstackRead,
            update_schema=OpenstackUpdate
        ),
        'saltstack': DatasourceRouterSchema(
            datasource_model=Saltstack,
            create_schema=SaltstackCreate,
            read_schema=SaltstackRead,
            update_schema=SaltstackUpdate,
        )
    }

    for label, schema in DATASOURCE_SCHEMAS.items():
        ds_router = schema.create_router(label)
    return ds_router
