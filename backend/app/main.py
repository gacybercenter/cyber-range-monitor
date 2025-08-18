import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import api_router, middleware
from app.core import settings
from app.infrastructure.db import DatabaseEngine
from app.infrastructure.log import setup_logging
from app.infrastructure.redis import RedisConnection

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used to match method signature


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the "yield"

    Arguments:
        app {FastAPI} -- the app instance, required even if not used
    """

    await DatabaseEngine.connect()
    await RedisConnection.connect()

    # ^ app startup

    yield

    # v app shutdown

    await DatabaseEngine.disconnect()
    await RedisConnection.disconnect()


def create_app() -> FastAPI:
    """
    Creates the FastAPI instance and returns the
    created app instance.

    Returns:
        FastAPI -- the API instance
    """
    setup_logging()
    config = settings.get_app_settings()
    logger = logging.getLogger(__name__)
    app = FastAPI(
        title=config.openapi.title,
        version=config.openapi.version,
        description=config.openapi.description,
        debug=config.debug,
        lifespan=lifespan,
        openapi_url=config.docs.openapi_url,
        docs_url=config.docs.docs_url,
        redoc_url=config.docs.redoc_url,
    )
    if app.debug:
        logger.warning('Debug mode is enabled, disable in production.')

    if not config.docs.allow_docs:
        app.openapi_url = None
        app.docs_url = None
        app.redoc_url = None
        logger.info('OpenAPI documentation is disabled.')
    else:
        logger.info('Documentation routes enabled, disable in production.')

    logger.info('App instance created, registering middleware and exception handlers.')
    middleware.register_middleware(app)
    logger.info('Middleware initialized, adding API routes.')

    app.include_router(api_router)

    logger.info('API routes registered successfully, app build successful.')
    return app
