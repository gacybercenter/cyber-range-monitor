from fastapi.routing import APIRoute

# NOTE: This file helps for creating the OpenAPI spec for the backend and may seem
# like a lot of boilerplate but it helps when creating axios client from the OpenAPI spec
# because without it, the service names created for the routes are verbose (e.g "eventLogReadSummaryGetGet")
# to eventLogs.getSummary()
# From Official Documentation: https://fastapi.tiangolo.com/advanced/generate-clients/#client-method-names


def create_operation_id(route: APIRoute) -> str:
    """Generates a unique id for the route to help normalize
    the API service names.
    https://fastapi.tiangolo.com/advanced/generate-clients/#custom-generate-unique-id-function
    Returns:
        str -- the adjusted operation ID
    """
    return f"{route.tags[0]}-{route.name}"
