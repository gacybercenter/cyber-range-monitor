import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from range_monitor import api, config, error_handler, middleware
from range_monitor.infra import log
from range_monitor.lifespan import create_api_context

logger = logging.getLogger(__name__)

def disable_doc_routes(app: FastAPI) -> None:
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None


def configure_app(app: FastAPI) -> None:
    '''
    setups the FastAPI instance by including the routes, middleware, and error handlers.

    Parameters
    ----------
    app : FastAPI
    settings : config.AppSettings
    '''
    settings = config.get_app_settings()


    if not settings.app.options.allow_docs:
        logger.info('Notice: Swagger docs have been disabled.')
        disable_doc_routes(app)
    else:
        logger.warning(
            'Warning: Swagger docs are enabled, disable in production'
        )

    logger.info('Adding application routes, middleware, and error handlers.')

    middleware.register_middleware(app, settings.cors)
    error_handler.add_handlers(app)

    app.include_router(api.create_router())
    logger.info('Application configuration complete.')


@asynccontextmanager
async def asgi_lifespan(app: FastAPI):
    '''
    The lifespan context manager for the FastAPI application,
    defining what happens with each worker on startup and shutdown
    and yields a dictionary of what can then be accessed in routes via
    `request.state`.

    Parameters
    ----------
    app : FastAPI

    Yields
    ------
        _A dictionary of the resources available on each request_
    '''
    settings = config.get_app_settings()
    context = create_api_context(settings)

    try:
        await context.setup()
        yield context.share()
    finally:
        await context.dispose()


def create_app(settings: config.AppSettings | None = None) -> FastAPI:
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

    settings = settings or config.get_app_settings()
    log.setup_logger(settings.logger)

    app = FastAPI(
        title=settings.app.title,
        description=settings.app.description,
        summary=settings.app.summary,
        docs_url=settings.app.docs_url,
        redoc_url='/redoc',
        openapi_url='/openapi.json',
        version=settings.app.version,
        debug=settings.app.options.debug,
        lifespan=asgi_lifespan,
    )

    configure_app(app)

    return app
