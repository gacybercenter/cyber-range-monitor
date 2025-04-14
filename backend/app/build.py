from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.extensions import api_console

from app.core.db.main import connect_db, get_session


from app.extensions.redis.connection import RedisConnection
from app.extensions.openapi_extra import create_operation_id
from app.extensions.logging.config import setup_api_logging
from app.extensions import event_logger


# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used to match method signature


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    '''Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the "yield"

    Arguments:
        app {FastAPI} -- the app instance, required even if not used
    '''
    setup_api_logging()
    await connect_db()
    await RedisConnection.connect()
    async with get_session() as session:
        await event_logger.info("Database connected, starting API...", session)
    yield
    async with get_session() as session:
        await event_logger.info("Shutting down API...", session)
        await session.commit()
        await session.close()
    await RedisConnection.disconnect()


def create_instance() -> FastAPI:
    '''creates the fastapi app instance

    Returns:
        FastAPI -- the API instance
    '''
    config_yml = config.get_config_yml()
    app_config = config_yml.app
    project = config.get_pyproject()

    return FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=app_config.debug,
        lifespan=life_span,
        generate_unique_id_function=create_operation_id
    )


def handle_documentation(app: FastAPI) -> None:
    '''determines whether or not to add documentation to the app 
    instance

    Arguments:
        app {FastAPI} -- the app instance
    '''
    doc_config = config.get_config_yml().documentation
    if not doc_config.allowed:
        return
    api_console.debug('Registering documentation...')
    app.openapi_url = doc_config.openapi_json_url
    app.docs_url = doc_config.swagger_url
    app.redoc_url = doc_config.redoc_url


def register_cors(app: FastAPI) -> None:
    '''creates the CORS middleware based on the config

    Returns:
        CORSMiddleware -- the cors middle ware instance
    '''
    cors_init = config.get_config_yml().cors
    app.add_middleware(
        CORSMiddleware,
        **cors_init.model_dump()
    )
