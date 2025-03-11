from fastapi import APIRouter

from .router_setup import datasource_router
from .schema import (
    GuacamoleCreateForm,
    GuacamoleRead,
    GuacamoleUpdateForm,
    OpenstackCreateForm,
    OpenstackRead,
    OpenstackUpdateForm,
    SaltstackCreateForm,
    SaltstackRead,
    SaltstackUpdateForm,
)
from app.extensions import api_console
from .model import Guacamole, Openstack, Saltstack

from app.extensions.openapi_extra import APITags


def create_datasource_router() -> APIRouter:
    """Creates the API Router for all of the Datasources
    using ROUTER_SCHEMAS to define the response, body
    for requests and the associated ORM for the
    'create_data_source_router' factory function

    This allows all of the datasources to share the same
    prefix, handle all requests identically (minus the request bodies)
    with the benefit of custom validation for each of the expected request
    bodies


    Returns:
        APIRouter -- the datasource API router
    """
    ds_router = APIRouter(prefix="/datasources")
    ROUTER_SCHEMAS = {
        "guacamole": {
            "create_schema": GuacamoleCreateForm,
            "read_schema": GuacamoleRead,
            "update_schema": GuacamoleUpdateForm,
            "datasource_model": Guacamole,
            "tag_name": APITags.guac
        },
        "openstack": {
            "create_schema": OpenstackCreateForm,
            "read_schema": OpenstackRead,
            "update_schema": OpenstackUpdateForm,
            "datasource_model": Openstack,
            "tag_name": APITags.openstack
        },
        "saltstack": {
            "create_schema": SaltstackCreateForm,
            "read_schema": SaltstackRead,
            "update_schema": SaltstackUpdateForm,
            "datasource_model": Saltstack,
            "tag_name": APITags.saltstack
        },
    }

    for label, schema in ROUTER_SCHEMAS.items():
        datasource_init = {"datasource_name": label, **schema}
        api_console.prints(
            f"\t[italic green]Adding Datasource Router -> /{label}[/italic green]"
        )
        router = datasource_router(**datasource_init)
        ds_router.include_router(router)

    return ds_router
