from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rich.traceback import install

from app.extensions import api_console
from app.configs import running_app_config, running_project
from app.db.main import connect_db, get_session
from app.extensions.middleware import register_middleware
from app.routers import register_routers

install(show_locals=True)

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used


async def on_startup(app: FastAPI) -> None:
    await connect_db()
    async with get_session() as session:
        await api_console.info('Database connected, starting API...', session)

async def on_shutdown(app: FastAPI) -> None:
    async with get_session() as session:
        await api_console.info('Shutting down API...', session)
        await session.commit()
        await session.close()


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup(app)
    yield
    await on_shutdown(app)

def create_app() -> FastAPI:
    project = running_project()
    app_config = running_app_config()
    
    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=app_config.DEBUG,
        lifespan=life_span
    )

    if app_config.ALLOW_DOCUMENTATION:
        docs = app_config.api_doc_urls()
        app.redoc_url = docs['redoc']
        app.openapi_url = docs['openapi']
        app.docs_url = docs['swagger']
    
    api_console.debug('Registering middleware...')
    register_middleware(app)
    api_console.debug('Middleware registered, registering routers...')
    register_routers(app)

    return app
