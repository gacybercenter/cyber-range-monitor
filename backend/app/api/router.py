from fastapi import APIRouter
from .auth.router import auth_router
from .datasources import router as ds_routers
from .users.router import user_router
from .health.router import health_router

from app.utils.openapi_extra.utils import create_operation_id
from app.utils.openapi_extra.responses import SchemaError, ErrorDoc, APIResponses


api_router = APIRouter(
    prefix="/api",
    generate_unique_id_function=create_operation_id,
    responses=APIResponses(
        [
            ErrorDoc("API fails internally", 500, title="Internal Server Error"),
            SchemaError("Request Body is invalid", title="Schema Error"),
        ]
    ),
)

# ** Auth **
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
# ** Users **
api_router.include_router(user_router, prefix="/users", tags=["Users"])

# ** Datasources 'Guac', 'OpenStack', 'SaltStack' **
DATASOURCE_ROUTER_PREFIX = "/datasources"
api_router.include_router(
    ds_routers.guac_router, prefix=f"{DATASOURCE_ROUTER_PREFIX}/guac", tags=["Guac"]
)
api_router.include_router(
    ds_routers.open_stack_router,
    prefix=f"{DATASOURCE_ROUTER_PREFIX}/openstack",
    tags=["Openstack"],
)
api_router.include_router(
    ds_routers.salt_stack_router,
    prefix=f"{DATASOURCE_ROUTER_PREFIX}/saltstack",
    tags=["Saltstack"],
)


# health router
api_router.include_router(health_router, prefix="/health", tags=["Health"])
