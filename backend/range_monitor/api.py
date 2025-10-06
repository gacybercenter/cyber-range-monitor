from typing import Dict

from fastapi import APIRouter, status

from range_monitor.utils.openapi_extra import Error, create_operation_id
from range_monitor.utils.response_class import MsgspecJsonResponse


def create_router() -> APIRouter:
    '''
    Creates the main API router and includes all
    sub-routers.
    '''
    from range_monitor.auth.router import auth_router
    from range_monitor.guac.router import guac_api_router
    from range_monitor.sources.router import (
        guac_router,
        openstack_router,
        saltstack_router,
    )
    from range_monitor.users.router import users_router

    router = APIRouter(
        default_response_class=MsgspecJsonResponse,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: Error('Validation error'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: Error('Internal server error'),
        },
        generate_unique_id_function=create_operation_id,
    )

    # auth, for login and logout
    router.include_router(
        auth_router,
        prefix='/auth',
        tags=['Authentication'],
    )

    auth_errors: Dict = {
        status.HTTP_401_UNAUTHORIZED: Error('Unauthorized'),
        status.HTTP_403_FORBIDDEN: Error('Forbidden'),
    }

    # users, requires auth
    router.include_router(
        users_router,
        prefix='/users',
        tags=['Users'],
        responses=auth_errors,
    )

    datasource_router = APIRouter(
        prefix='/sources',
        responses=auth_errors,
    )


    datasource_router.include_router(
        openstack_router,
        prefix='/openstack',
        tags=['Openstack'],
    )

    datasource_router.include_router(
        guac_router,
        prefix='/guacamole',
        tags=['Guacamole'],
    )

    datasource_router.include_router(
        saltstack_router,
        prefix='/saltstack',
        tags=['Saltstack'],
    )

    router.include_router(datasource_router)

    router.include_router(
        guac_api_router,
        prefix='/guacamole/api',
        tags=['Guacamole API'],
        responses={
            **auth_errors,
            status.HTTP_503_SERVICE_UNAVAILABLE: Error('Guacamole not connected'),
            status.HTTP_409_CONFLICT: Error('State of datasource is unreachabled')
        },
    )


    return router
