import os
from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rich.traceback import install

from app.common import console
from app.common.logging import LogWriter
from app.config import Settings, running_config
from app.db import connect_db, get_session
from app.middleware import register_middleware
from app.routers import register_routers

logger = LogWriter('APP')
install(show_locals=True)

# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used


async def on_startup(app: FastAPI) -> None:
    await connect_db()
    async with get_session() as session:
        await logger.info('Build successful and API is running', session)
        await session.commit()
        await session.close()


async def on_shutdown(app: FastAPI) -> None:
    async with get_session() as session:
        await logger.info('Shutting down API...', session)
        await session.commit()
        await session.close()


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup(app)
    yield
    await on_shutdown(app)


def register_docs(app: FastAPI) -> None:
    app.redoc_url = '/redoc'
    app.openapi_url = '/openapi.json'
    app.docs_url = '/docs'


def create_app() -> FastAPI:
    console.print(
        f'[italic green]Running API under APP_ENV={os.getenv('APP_ENV')}[/italic green]'
    )
    Settings.load()
    settings = running_config()
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=life_span
    )
    if settings.ALLOW_DOCUMENTATION:
        console.print(
            '[bold red]Note: Documentation is enabled [/bold red]'
            '[bold red]\nDisable in production[/bold red]'
            '\t[bold]Swagger UI: [/bold] /docs\n'
            '\t[bold]OpenAPI JSOM: [/bold] /openapi.json\n'
            '\t[bold]Redoc: [/bold] /redoc\n'
        )
        register_docs(app)
    register_middleware(app)
    register_routers(app)

    return app
