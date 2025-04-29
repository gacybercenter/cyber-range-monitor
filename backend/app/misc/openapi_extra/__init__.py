from .main import APITags, create_operation_id
# custom_openapi_schema
from .responses import (
    err_response_doc, 
    AUTH_DEP_RESPONSES,
    USER_DEP_RESPONSE,
    ROLE_REQUIRED_DEP_RESPONSE,
    NOT_FOUND_404,
    GLOBAL_ERROR_RESPONSES
)

OPENAPI_JSON_PATH = "/openapi.json"
SWAGGER_PATH = "/docs"
REDOC_PATH = "/redoc"

__all__ = [
    "APITags",
    "create_operation_id",
    # "custom_openapi_schema",
    "err_response_doc",
    "AUTH_DEP_RESPONSES",
    "USER_DEP_RESPONSE",
    "ROLE_REQUIRED_DEP_RESPONSE",
    "NOT_FOUND_404",
    "OPENAPI_JSON_PATH",
    "SWAGGER_PATH",
    "REDOC_PATH",
    'GLOBAL_ERROR_RESPONSES',
]
