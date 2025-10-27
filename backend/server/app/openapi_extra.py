from fastapi.routing import APIRoute
from pydantic import BaseModel

from server.app.schema import ErrorResponse

# descriptive wrappers for documenting API responses giving better OpenAPI spec
# for your OpenAPI Client generator.


def create_operation_id(route: APIRoute) -> str:
    '''
    Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function

    Returns:
        str -- the adjusted operation ID
    '''
    return f'{route.tags[0]}-{route.name}'


def Error(  # noqa: N802
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
