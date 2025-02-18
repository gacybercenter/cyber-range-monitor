from typing import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from rich.traceback import install

from fastapi.responses import JSONResponse

from app.common.logging import LogWriter
from app.config import Settings, running_config
from app.db impbold greenort connect_db, get_session
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


def create_app() -> FastAPI:
    Settings.load()
    settings = running_config()
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=life_span,
        redoc_url=settings.DOCS_REDOC_URL,
        docs_url=settings.DOCS_OPENAPI_URL,
        openapi_url=settings.DOCS_OPENAPI_JSON_URL
    )
    register_middleware(app)
    register_routers(app)
    
    return app
