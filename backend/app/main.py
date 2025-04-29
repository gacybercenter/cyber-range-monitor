from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.db.main import connect_database, disconnect_database
from app.plugins.redis import redis_client

from app.misc.openapi_extra import (
    GLOBAL_ERROR_RESPONSES,
    create_operation_id,
    OPENAPI_JSON_PATH,
    REDOC_PATH,
    SWAGGER_PATH
)
from app.misc.msg_spec_json import MsgSpecJSONResponse

from app.core.settings import app_settings, get_pyproject
from app.core.logs import setup_logging
from app.plugins.redis import redis_client

from app import middleware, api

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used to match method signature


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    '''Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the "yield"

    Arguments:
        app {FastAPI} -- the app instance, required even if not used
    '''

    await connect_database()
    await redis_client.open()

    # ^ app startup

    yield

    # v app shutdown

    await disconnect_database()
    await redis_client.close()


def create_app() -> FastAPI:
    '''Creates the FastAPI instance and returns the 
    created app instance.

    Returns:
        FastAPI -- the API instance
    '''
    setup_logging()

    log = logging.getLogger(__name__)
    log.info('Logging setup, building application.')
    project = get_pyproject()

    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=app_settings.debug,
        lifespan=lifespan,
        generate_unique_id_function=create_operation_id,
        responses=GLOBAL_ERROR_RESPONSES,
        default_response_class=MsgSpecJSONResponse
    )

    log.info('App instance created.\n')

    if app_settings.allow_documentation:
        app.openapi_url = OPENAPI_JSON_PATH
        app.redoc_url = REDOC_PATH
        app.docs_url = SWAGGER_PATH
        log.warning(
            'API documentation is enabled: Disable in production'
        )
    else:
        app.openapi_url = None
        app.redoc_url = None
        app.docs_url = None
        log.info(
            'API documentation routes are [bold green]disabled[/bold green]'
        )

    middleware.register_middleware(app)
    log.info(
        '\nMiddleware setup complete, adding exception handlers to API\n'
    )
    api.register_routes(app)
    log.info('API routes initialized, API setup complete.\n')
    return app
