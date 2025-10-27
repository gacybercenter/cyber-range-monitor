import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import APIRouter, FastAPI, status

from server.app.errors.handlers import register_exception_handlers
from server.logger import configure_logging
from server.middleware import register_middleware
from server.response import MsgspecJsonResponse
from server.settings import get_app_settings

logger = logging.getLogger(__name__)


def configure_app(app: FastAPI) -> None:
    '''
    setups the FastAPI instance by including the routes, middleware, and error handlers.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance to configure.
    '''
    settings = get_app_settings()

    if not settings.app.allow_docs:
        logger.info('Notice: Swagger docs have been disabled.')
        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None
    else:
        logger.warning('Warning: Swagger docs are enabled, disable in production')

    logger.info('Adding application routes, middleware, and error handlers.')

    register_middleware(app, settings.cors)
    register_exception_handlers(app)
    register_api_routers(app)

    logger.info('Application configuration complete.')


@asynccontextmanager
async def asgi_lifespan(app: FastAPI):  # noqa: ANN201
    '''
    The lifespan context manager for the FastAPI application,
    defining what happens with each worker on startup and shutdown
    and yields a dictionary of what can then be accessed in routes via
    `request.state`.
    '''
    from server.app import lifespan

    await lifespan.on_startup()

    try:
        yield
    finally:
        await lifespan.on_shutdown()


def create_app() -> FastAPI:
    '''
    Creates and configures a FastAPI instance.

    Parameters
    ----------
    version : str
    debug : bool, optional
        _Debug mode is enabled or not_, by default False

    Returns
    -------
    FastAPI
    '''
    settings = get_app_settings()

    configure_logging(settings.logger)

    app = FastAPI(
        title=settings.app.title,
        description=settings.app.description,
        summary=settings.app.summary,
        docs_url=settings.app.docs_url,
        redoc_url=settings.app.redoc_url,
        openapi_url=settings.app.openapi_url,
        version=settings.app.version,
        debug=settings.app.debug,
        lifespan=asgi_lifespan,
    )

    configure_app(app)

    return app


def register_api_routers(app: FastAPI) -> None:
    '''
    Adds all API routers to the FastAPI application.
    '''
    from server.app.auth.router import auth_router
    from server.app.data_sources.routers import (
        guac_router,
        openstack_router,
        saltstack_router,
    )
    from server.app.guac.router import guac_api_router
    from server.app.openapi_extra import Error, create_operation_id
    from server.app.users.router import users_router

    root_router = APIRouter(
        default_response_class=MsgspecJsonResponse,
        generate_unique_id_function=create_operation_id,
        responses={
            status.HTTP_422_UNPROCESSABLE_ENTITY: Error('Validation Error'),
            status.HTTP_500_INTERNAL_SERVER_ERROR: Error('Internal Server Error'),
        },
    )

    # /auth
    root_router.include_router(
        auth_router,
        prefix='/auth',
        tags=['Authentication'],
    )

    auth_errors: Any = {
        status.HTTP_401_UNAUTHORIZED: Error('Authentication required'),
        status.HTTP_403_FORBIDDEN: Error('Insufficient permissions'),
    }

    # /users
    root_router.include_router(
        users_router,
        prefix='/users',
        tags=['Users'],
        responses=auth_errors,
    )

    # /data_sources/guacamole
    root_router.include_router(
        guac_router,
        prefix='/data_sources/guacamole',
        tags=['Guacamole Data Sources'],
        responses=auth_errors,
    )

    # /data_sources/openstack
    root_router.include_router(
        openstack_router,
        prefix='/data_sources/openstack',
        tags=['OpenStack Data Sources'],
        responses=auth_errors,
    )

    # /data_sources/saltstack
    root_router.include_router(
        saltstack_router,
        prefix='/data_sources/saltstack',
        tags=['Saltstack Data Sources'],
        responses=auth_errors,
    )

    # /guacamole
    root_router.include_router(
        guac_api_router,
        prefix='/guacamole',
        tags=['Guacamole API'],
        responses=auth_errors,
    )

    app.include_router(root_router)
