from fastapi.routing import APIRoute
from pydantic import BaseModel

from range_monitor.schema.errors import ErrorResponse

# A descriptive wrappers for documenting API responses for better OpenAPI spec generation
# for your OpenAPI Client generator.


def create_operation_id(route: APIRoute) -> str:
    """
    Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function

    Returns:
        str -- the adjusted operation ID
    """
    return f'{route.tags[0]}-{route.name}'


def Error(
    description: str,
    *,
    model: type[BaseModel] | None = None,
    headers: dict | None = None,
) -> dict:
    '''
    Convience wrapper for annotating api routes with
    error response models for better OpenAPI spec generation.
    '''
    if not model:
        model = ErrorResponse

    return {
        'model': model,
        'description': description,
        'headers': headers or {},
    }

