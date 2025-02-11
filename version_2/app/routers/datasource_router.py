from fastapi import APIRouter
from app.models import Guacamole, Openstack, Saltstack
from app.schemas import (
    GuacamoleCreate, GuacamoleRead, GuacamoleUpdate,
    OpenstackCreate, OpenstackRead, OpenstackUpdate,
    SaltstackCreate, SaltstackRead, SaltstackUpdate
)
from app.routers.misc.datasource_factory import DatasourceRouterSchema


def initialize_router() -> APIRouter:
    '''Creates the API Router for all of the Datasources
    using DATASOURCE_SCHEMAS to define the response, body 
    for requests and the associated ORM for the  
    'create_data_source_router' factory function 

    This allows all of the datasources to share the same 
    prefix, handle all requests identically (minus the request bodies)  
    with the benefit of custom validation for each of the expected request
    bodies
    
    
    Returns:
        APIRouter -- the datasource API router
    '''
    ds_router = APIRouter(
        prefix='/datasources'
    )
    DATASOURCE_SCHEMAS = {
        'guacamole': DatasourceRouterSchema(
            datasource_model=Guacamole,
            create_schema=GuacamoleCreate,
            read_schema=GuacamoleRead,
            update_schema=GuacamoleUpdate
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
        sub_router = schema.create_router(label)
        ds_router.include_router(sub_router)
        
    return ds_router
