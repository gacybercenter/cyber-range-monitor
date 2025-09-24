


from fastapi import APIRouter, status

from range_monitor.utils.openapi_extra import api_error, create_operation_id
from range_monitor.utils.response_class import MsgspecJsonResponse


def create_routes() -> APIRouter:
    '''
    Creates the main API router and includes all
    sub-routers.
    '''
    from range_monitor.api.tokens import tokens_router
    from range_monitor.api.user import users_router


    router = APIRouter(
        default_response_class=MsgspecJsonResponse,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: api_error('Validation error'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: api_error('Internal server error'),
        },
        generate_unique_id_function=create_operation_id,
    )
    # auth, for login and logout
    router.include_router(
        tokens_router,
        prefix='/auth',
        tags=['Authentication'],
    )


    # users, requires auth and admin privileges
    router.include_router(
        users_router,
        prefix='/users',
        tags=['Users'],
    )



    return router