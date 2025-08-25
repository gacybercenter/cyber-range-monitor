from contextlib import asynccontextmanager

from fastapi import FastAPI
import logging
from monitor_api.core import constant, settings
from monitor_api.infra import APIAdapters, APILogger, APISecurity
from monitor_api.app import middleware, error_handler, router


@asynccontextmanager
async def asgi_lifespan(app: 'FastAPI'):
    APILogger.configure(
        stdout=True, security_logger=True, error_logger=True, service_logger=True
    )
    logger = APILogger.get_loguru_logger()
    logger.log('LIFESPAN', 'Logging configured, ASGI lifespan starting up...')

    adapters = APIAdapters.build()
    logger.log('LIFESPAN', 'Sucessfully built adapters.')
    security = APISecurity.build()
    logger.log('LIFESPAN', 'Sucessfully built security services.')
    try:
        logger.log('LIFESPAN', 'Connecting API adapters...')
        await adapters.connect_all()
        logger.log(
            'LIFESPAN',
            'All adapters connected successfully, mounting resources to app state.',
        )
        app.state.adapters = adapters
        app.state.security = security
        logger.log('LIFESPAN', 'ASGI lifespan started successfully.')
        yield
    finally:
        logger.log('LIFESPAN', 'ASGI lifespan shutting down, disconnecting adapters...')
        await adapters.disconnect_all()
        logger.log('LIFESPAN', 'All adapters disconnected, disposing loggers...')
        APILogger.dispose()


def create_app() -> FastAPI:
    config = settings.get_adapter_settings().app
    app = FastAPI(
        title=constant.APP_TITLE,
        description=constant.APP_DESCRIPTION,
        summary=constant.APP_SUMMARY,
        docs_url=constant.DOCS_URL,
        redoc_url=constant.REDOC_URL,
        openapi_url=constant.OPENAPI_URL,
        version=config.version,
        debug=config.debug,
        lifespan=asgi_lifespan,
    )
    logger = logging.getLogger(__name__)  # api logger not yet available
    logger.info('FastAPI insatnce created, configuring app...')
    if not config.allow_docs:
        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None
        logger.info('Note: API documentation is disabled.')
    else:
        logger.warning('Note: API documentation is enabled; disable in production')

    logger.info('Mounting middleware and exception handlers...')
    middleware.mount_middleware(app)
    error_handler.mount_exception_handlers(app)

    logger.info('Registering API routes')

    app.include_router(router.api_router)
    logger.info('App configuration complete.')

    return app
