from fastapi import APIRouter, status

from ..utils.openapi_extra import HTTPError, create_operation_id
from ..utils.response_class import MsgSpecJSONResponse
from .routes import auth_router, user_router

api_router = APIRouter(
    prefix='/api',
    generate_unique_id_function=create_operation_id,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: HTTPError('Validation error'),
        status.HTTP_500_INTERNAL_SERVER_ERROR: HTTPError('Internal server error'),
    },
    default_response_class=MsgSpecJSONResponse,
)

# ** Auth **
api_router.include_router(auth_router, prefix='/auth', tags=['Auth'])
# ** Users **
auth_protected_errors = {
    status.HTTP_401_UNAUTHORIZED: HTTPError('User not authenticated'),
    status.HTTP_403_FORBIDDEN: HTTPError('User does not have permission'),
}

api_router.include_router(
    user_router,
    prefix='/users',
    tags=['Users'],
    responses=auth_protected_errors,  # type: ignore
)


# ** Datasources 'Guac', 'OpenStack', 'SaltStack' **
DATASOURCE_ROUTER_PREFIX = '/datasources'
# api_router.include_router(
#     ds_routers.guac_router, prefix=f"{DATASOURCE_ROUTER_PREFIX}/guac", tags=["Guac"]
# )
# api_router.include_router(
#     ds_routers.open_stack_router,
#     prefix=f"{DATASOURCE_ROUTER_PREFIX}/openstack",
#     tags=["Openstack"],
# )
# api_router.include_router(
#     ds_routers.salt_stack_router,
#     prefix=f"{DATASOURCE_ROUTER_PREFIX}/saltstack",
#     tags=["Saltstack"],
# )


# # health router
# api_router.include_router(health_router, prefix="/health", tags=["Health"])
