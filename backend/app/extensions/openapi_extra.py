from enum import StrEnum

from fastapi.routing import APIRoute


# NOTE: This file helps for creating the OpenAPI spec for the backend and may seem
# like a lot of boilerplate but it helps when creating axios client from the OpenAPI spec
# because without it, the service names created for the routes are verbose (e.g "eventLogReadSummaryGetGet")
# to eventLogs.getSummary()
# From Ofiical Documentation: https://fastapi.tiangolo.com/advanced/generate-clients/#client-method-names


class APITags(StrEnum):
    '''Represents the tags for the API documentation,
    this helps when creating the axios client from the OpenAPI spec
    and to keep things organized

    When you create a new route, make sure you add the tag here, it 
    helps with the OpenAPI spec and the axios client generation.
    '''
    user = 'user'
    auth = 'auth'
    event_logs = 'event_logs'
    openstack = 'openstack'
    guac_source = 'guac_datasource'
    saltstack_source = 'saltstack_datasource'
    openstack_source = 'openstack_datasource'
    
    

def create_operation_id(route: APIRoute) -> str:
    '''Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function
    Returns:
        str -- _description_
    '''
    return f"{route.tags[0]}-{route.name}"

def define_response(status_code: int, description: str) -> dict:
    '''Defines the response for the OpenAPI spec
    Returns:
        dict -- _description_
    '''
    return {status_code: {"description": description}}