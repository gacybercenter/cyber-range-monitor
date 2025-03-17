from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app import config

from app.core.db.main import connect_db, get_session

from app.extensions import api_console
from app.extensions.redis.connection import RedisConnection
from app.extensions.openapi_extra import create_operation_id


# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used
@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    '''Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the "yield"

    Arguments:
        app {FastAPI} -- the app instance, required even if not used
    '''
    await connect_db()
    await RedisConnection.connect()
    api_console.prints("Redis is connected")
    async with get_session() as session:
        await api_console.info("Database connected, starting API...", session)
    yield
    api_console.clears()
    async with get_session() as session:
        await api_console.info("Shutting down API...", session)
        await session.commit()
        await session.close()
    await RedisConnection.disconnect()


def register_middleware(app: FastAPI) -> None:
    """adds middleware to the app instance

    Arguments:
        app {FastAPI} -- the app instance
        use_security_headers {bool} -- from the config.yml app.use_security_headers
    """
    from app.extensions.middleware import (
        register_exc_handlers,
        RequestLoggingMiddleware,
    )

    cors_policy = config.get_config_yml().cors
    api_console.debug("Registering CORS Policy...")

    cors_init = cors_policy.model_dump()
    app.add_middleware(CORSMiddleware, **cors_init)

    api_console.debug("Registering request logging middleware...")
    app.add_middleware(RequestLoggingMiddleware)  # type: ignore
    api_console.debug("Registering exception handlers...")
    register_exc_handlers(app)


def create_instance() -> FastAPI:
    '''creates the fastapi app instance

    Returns:
        FastAPI -- _description_
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
