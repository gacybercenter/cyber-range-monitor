import logging
from contextlib import asynccontextmanager
from venv import logger

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from range_monitor import api, config, constant, log
from range_monitor.core.exceptions import APIException
from range_monitor.exception_handler import ExceptionHandlers
from range_monitor.lifespan import ServerContext
from range_monitor.middleware import AccessMiddleware, correlation_id_generator


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
    _LifespanResources_
        _A typed dictionary of the resources available on each request_
    '''

    settings = config.get_app_settings()
    context = ServerContext(is_testing=settings.app.testing)
    context.open_connections(settings=settings)
    await context.connect()
    try:
        resources = context.resources
        logger.info('App startup complete, resources: %s', resources)
        shared = resources.share()
        yield shared
        logger.info('App shutdown initiated...')
    except Exception as e:
        logger.error('Error during app lifespan: %s', e, exc_info=True)
        raise e
    finally:
        await context.disconnect()


def create_fastapi(
    *,
    version: str,
    debug: bool = False,
) -> FastAPI:
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
    return FastAPI(
        title=constant.APP_TITLE,
        description=constant.APP_DESCRIPTION,
        summary=constant.APP_SUMMARY,
        docs_url=constant.DOCS_URL,
        redoc_url=constant.REDOC_URL,
        openapi_url=constant.OPENAPI_URL,
        version=version,
        debug=debug,
        lifespan=asgi_lifespan,
    )


def mount_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        APIException,
        ExceptionHandlers.api_exception,  # type: ignore
    )
    app.add_exception_handler(
        RequestValidationError,
        ExceptionHandlers.request_validation_error,  # type: ignore
    )
    app.add_exception_handler(
        StarletteHTTPException,
        ExceptionHandlers.starlette_http_exception,  # type: ignore
    )
    app.add_exception_handler(Exception, ExceptionHandlers.general_exception)

def mount_middleware(
    app: FastAPI,
    *,
    cors_config: config.CorsConfig
) -> None:
    """
    Registers necessary middleware to the FastAPI app.

    Parameters
    ----------
    app : FastAPI
    """
    app.add_middleware(CORSMiddleware, **cors_config.model_dump())
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name=constant.REQUEST_ID_HEADER_NAME,
        update_request_header=True,
        generator=correlation_id_generator,
    )
    app.add_middleware(AccessMiddleware)

def disable_doc_routes(app: FastAPI) -> None:
    '''
    Disables the automatic API documentation routes.

    Parameters
    ----------
    app : FastAPI
    '''
    app.docs_url = None
    app.redoc_url = None
    app.openapi_url = None


def create_app(*, overrides: config.RangeMonitorSettings | None = None) -> FastAPI:
    '''
    Creates and configures the FastAPI application.

    Parameters
    ----------
    overrides : config.RangeMonitorSettings | None, optional
        _Optional settings to use instead of the ones loaded from the
        file system_, by default None

    Returns
    -------
    FastAPI
    '''
    log.configure_logging()
    logger = logging.getLogger(__name__)
    settings = overrides or config.get_app_settings()

    app = create_fastapi(
        version=settings.app.version,
        debug=settings.app.debug,
    )

    logger.info('FastAPI insatnce created, configuring app...')
    if not settings.app.allow_docs:
        disable_doc_routes(app)
        logger.info('API documentation is disabled.')
    else:
        logger.warning('API documentation is enabled, disable in production.')

    logger.info('Mounting middleware and exception handlers...')

    mount_middleware(app, cors_config=settings.cors)
    mount_exception_handlers(app)
    logger.info('Registering API routes...')

    app.include_router(api.create_routes())

    logger.info('App configuration complete.')
    return app
