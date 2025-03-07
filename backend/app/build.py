from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from rich.traceback import install

from app import config

from app.core.db.main import connect_db, get_session

from app.extensions import api_console
from app.extensions.middleware import register_middleware
from app.extensions import redis_client

from app.extensions.openapi_extra import create_operation_id

install(show_locals=True)

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await connect_db()
    await redis_client.is_connected()
    api_console.prints("Redis is connected")
    async with get_session() as session:
        await api_console.info("Database connected, starting API...", session)
    yield
    api_console.clears()
    async with get_session() as session:
        await api_console.info("Shutting down API...", session)
        await session.commit()
        await session.close()


def register_routers(app: FastAPI) -> None:
    '''adds all of the routers to the app instance 

    Arguments:
        app {FastAPI} -- the app to add the routers to 
    '''
    from app.users.router import user_router
    from app.auth.router import auth_router
    from app.logging.router import log_router
    from app.datasources.router import create_datasource_router
    
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(log_router)
    datasource_router = create_datasource_router()
    app.include_router(datasource_router)
    
    



def create_app() -> FastAPI:
    '''creates the fastapi app instance 

    Returns:
        FastAPI -- _description_
    '''
    project = config.get_pyproject()
    app_config = config.get_app_config()

    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=app_config.debug,
        lifespan=life_span,
        generate_unique_id_function=create_operation_id
    )

    docs_config = config.get_documentation_config()
    if docs_config.allowed:
        docs_config.register_docs(app)

    api_console.debug("Registering middleware...")
    register_middleware(app)
    api_console.debug("Middleware registered, registering routers...")
    register_routers(app)

    return app