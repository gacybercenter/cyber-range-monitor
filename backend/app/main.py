from fastapi import FastAPI

from . import app_builder
from app import config

from app.misc import openapi_extra
from app.misc.logging import APILogging

from app import domains


def create_app() -> FastAPI:
    '''Creates the FastAPI instance and returns the 
    created app instance.

    Returns:
        FastAPI -- the API instance
    '''
    APILogging.setup()
    config_yml = config.get_config_yml()
    app_config = config_yml.app
    project = config.get_pyproject()

    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=app_config.debug,
        lifespan=app_builder.life_span,
        generate_unique_id_function=openapi_extra.create_operation_id,
        responses=openapi_extra.PYDANTIC_SCHEMA_ERROR
    )
    logger = APILogging.api()

    logger.info('API instance created.\n')

    if app_config.allow_documentation:
        app.openapi_url = openapi_extra.OPENAPI_JSON_PATH
        app.redoc_url = openapi_extra.REDOC_PATH
        app.docs_url = openapi_extra.SWAGGER_PATH
        logger.warning(
            'API documentation is enabled: [bold red]Disable in production[/bold red]'
        )
    else:
        app.openapi_url = None
        app.redoc_url = None
        app.docs_url = None
        logger.info(
            'API documentation routes are [bold green]disabled[/bold green]'
        )

    logger.info('Adding middleware to API...')

    app_builder.register_middleware(app)

    logger.info(
        '\nMiddleware setup complete, adding exception handlers to API\n')

    app_builder.register_exception_handlers(app)

    logger.info('Exception handlers setup complete, initializing API routes.\n')

    domains.register_api_routers(app)

    logger.info('API routes initialized, API setup complete.\n')

    return app


app = create_app()
