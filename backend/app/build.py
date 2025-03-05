from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from rich.traceback import install

from app import config
from app.db.main import connect_db, get_session
from app.extensions import api_console
from app.extensions.middleware import register_middleware
from app.extensions.redis import client
from app.routers import register_routers

install(show_locals=True)

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await connect_db()
    await client.is_connected()
    api_console.prints("Redis is connected")
    async with get_session() as session:
        await api_console.info("Database connected, starting API...", session)
    yield
    api_console.clears()
    async with get_session() as session:
        await api_console.info("Shutting down API...", session)
        await session.commit()
        await session.close()


def create_app() -> FastAPI:
    project = config.get_pyproject()
    config_yml = config.get_config_yml()

    app = FastAPI(
        title=project.name,
        version=project.version,
        description=project.description,
        debug=config_yml.app.debug,
        lifespan=life_span,
    )

    if config_yml.documentation.allowed:
        config_yml.documentation.register_docs(app)

    api_console.debug("Registering middleware...")
    register_middleware(app)
    api_console.debug("Middleware registered, registering routers...")
    register_routers(app)

    return app
