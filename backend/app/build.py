from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rich.traceback import install

from app.extensions import api_console
from app import settings
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
    project = settings.get_pyproject()
    api_config = settings.get_config_yml().api_config
    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=api_config.debug,
        lifespan=life_span
    )

    if api_config.docs_enabled():
       api_config.register_docs(app)
    
    api_console.debug('Registering middleware...')
    register_middleware(app, api_config.use_security_headers)
    api_console.debug('Middleware registered, registering routers...')
    register_routers(app)

    return app
