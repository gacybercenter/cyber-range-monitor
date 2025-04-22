from enum import StrEnum

from fastapi.routing import APIRoute

# NOTE: This file helps for creating the OpenAPI spec for the backend and may seem
# like a lot of boilerplate but it helps when creating axios client from the OpenAPI spec
# because without it, the service names created for the routes are verbose (e.g "eventLogReadSummaryGetGet")
# to eventLogs.getSummary()
# From Official Documentation: https://fastapi.tiangolo.com/advanced/generate-clients/#client-method-names


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
    datasource = 'datasource'
    
    guac = 'guacamole'
    openstack = 'openstack'
    saltstack = 'saltstack'

    

def create_operation_id(route: APIRoute) -> str:
    '''Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function
    Returns:
        str -- the adjusted operation ID
    '''
    return f"{route.tags[0]}-{route.name}"




# def custom_openapi_schema() -> dict:
#     '''Replaces the HTTPRequestValidationError (raised when pydantic validation fails)
#     with the proper model with the validation error details and returns the edited openapi
#     schema
#     Returns:
#         dict -- the modified OpenAPI schema with the proper validation error details 
#     '''
#     from app.main import app

#     openapi_schema: dict[str, dict[str, dict]] = app.openapi()

#     openapi_schema['components']['schemas']['ValidationError'] = HTTPValidationErrorDetails.model_json_schema()

#     for path in openapi_schema['paths'].values():
#         for operation in path.values():
#             if 'responses' in operation and '422' in operation['responses']:
#                 operation['responses']['422']['content']['application/json']['schema'] = {
#                     '$ref': '#/components/schemas/ValidationError'
#                 }

#     return openapi_schema
