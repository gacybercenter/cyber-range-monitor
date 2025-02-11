from re import DEBUG
from typing import AsyncGenerator, Callable, Optional
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.common.logging import LogWriter
from app.config.main import AppSettings, running_config
from app.db import connect_db, get_session
from app.middleware import register_middleware
from app.routers import register_routers

logger = LogWriter('APP')


# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used

async def on_startup(app: FastAPI) -> None:
    await connect_db()
    async with get_session() as session:
        await logger.info('Build successful and application started', session)
        await session.commit()
        await session.close()


async def on_shutdown(app: FastAPI) -> None:
    async with get_session() as session:
        await logger.info('Application is shutting down', session)
        await session.commit()
        await session.close()


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup(app)
    yield
    await on_shutdown(app)


def create_app(
    env: str = '.env',
) -> FastAPI:
    
    AppSettings.from_env(env)
    
    settings = running_config()
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description='An opensource application for monitoring Datasources developed by the Georgia Cyber Range with support for Guacamole, Openstack and Saltstack',
        debug=settings.DEBUG,
        lifespan=life_span
    )
    register_middleware(app)
    register_routers(app)

    return app
