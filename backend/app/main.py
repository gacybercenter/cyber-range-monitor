import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

from app.adapters import db, log, redis_client
from app.api import api_router
from app.core import settings
from app.middleware import AccessMiddleware, HttpExceptionHandler

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used to match method signature


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the
    "yield"
    """

    await db.connect_db()
    await redis_client.connect_redis()

    # ^ app startup

    yield

    # v app shutdown

    await db.disconnect_db()
    await redis_client.disconnect_redis()

def disable_docs(app: FastAPI) -> None:
    """
    Disables the OpenAPI documentation routes.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    """
    app.openapi_url = None
    app.docs_url = None
    app.redoc_url = None


def register_middleware(app: FastAPI, settings: settings.MiddlewareConfig) -> None:
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name=settings.correlation_id.HEADER_NAME,
        update_request_header=settings.correlation_id.UPDATE_REQUEST_HEADER,
    )
    app.add_middleware(
        AccessMiddleware,
        correlation_id_header=settings.correlation_id.HEADER_NAME,
    )
    HttpExceptionHandler.register(app)





def create_app() -> FastAPI:
    """
    Creates the FastAPI instance and returns the
    created app instance.

    Returns:
        FastAPI -- the API instance
    """
    log.setup_logging()
    logger = logging.getLogger(__name__)


    api_config = settings.get_api_settings()
    api_spec= settings.get_adapter_settings().openapi

    app = FastAPI(
        title=api_spec.title,
        description=api_spec.description,
        version=api_spec.version,
        openapi_url=api_spec.openapi_url,
        docs_url=api_spec.docs_url,
        redoc_url=api_spec.redoc_url,
        lifespan=lifespan,
        debug=api_config.app.DEBUG,
    )
    if app.debug:
        logger.warning('Debug mode is enabled, disable in production.')

    if not api_config.app.ALLOW_DOCS:
        disable_docs(app)
        logger.info('OpenAPI documentation is disabled.')
    else:
        logger.info('Documentation routes enabled, disable in production.')

    logger.info('App instance created, registering middleware and exception handlers.')

    register_middleware(app, api_config.middleware)

    logger.info('Middleware initialized, adding API routes.')

    app.include_router(api_router)

    logger.info('API routes registered successfully, app build successful.')

    return app
