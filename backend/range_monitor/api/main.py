

from typing import Dict

from fastapi import APIRouter, status

from range_monitor.utils.openapi_extra import api_error, create_operation_id
from range_monitor.utils.response_class import MsgspecJsonResponse


def create_routes() -> APIRouter:
    '''
    Creates the main API router and includes all
    sub-routers.
    '''
    from range_monitor.api.auth import auth_router
    from range_monitor.api.guacamole.sources import guac_source_router
    from range_monitor.api.open_stack.sources import openstack_source_router
    from range_monitor.api.profile import profile_router
    from range_monitor.api.user import users_router

    auth_protected_responses: Dict = {
        status.HTTP_401_UNAUTHORIZED: api_error('Not authenticated'),
        status.HTTP_403_FORBIDDEN: api_error('Invalid or expired session'),
    }

    router = APIRouter(
        default_response_class=MsgspecJsonResponse,
        responses={
            status.HTTP_404_NOT_FOUND: api_error('Non-existent route'),
            status.HTTP_422_UNPROCESSABLE_ENTITY: api_error('Validation error'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: api_error('Internal server error'),
        },
        generate_unique_id_function=create_operation_id,
    )
    # auth, for login and logout
    router.include_router(
        auth_router,
        prefix='/auth',
        tags=['Authentication'],
    )

    # profile, requires auth and is for a user to manage themself
    router.include_router(
        profile_router,
        prefix='/profile',
        responses=auth_protected_responses,
        tags=['profile']
    )

    # users, requires auth and admin privileges
    router.include_router(
        users_router,
        prefix='/users',
        tags=['Users'],
        responses=auth_protected_responses,
    )

    # guacamole
    guac_router = APIRouter(
        prefix='/guacamole',
    )

    guac_router.include_router(
        guac_source_router,
        prefix='/sources',
        tags=['guacamole'],
        responses=auth_protected_responses,
    )

    openstack_router = APIRouter(
        prefix='/openstack',
    )


    openstack_router.include_router(
        openstack_source_router,
        prefix='/sources',
        tags=['openstack'],
        responses=auth_protected_responses,
    )

    router.include_router(guac_router)
    router.include_router(openstack_router)


    return router