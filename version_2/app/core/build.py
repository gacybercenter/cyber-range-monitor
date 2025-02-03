from typing import AsyncGenerator, Callable, Optional
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.common.logging import LogWriter
from app.core.config.main import AppSettings, running_config
from .db import connect_db, get_session



logger = LogWriter('APP')


async def on_startup() -> None:
    await connect_db()
    async with get_session() as session:
        await logger.info('Build successful and application started', session)
        await session.commit()
        await session.close()


async def on_shutdown() -> None:
    async with get_session() as session:
        await logger.info('Application is shutting down', session)
        await session.commit()
        await session.close()

@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    await on_startup()
    yield 
    await on_shutdown()



async def create_app(
    builder: Optional[Callable] = None
) -> FastAPI:
    if builder is None:
        AppSettings.from_env()
    else:
        builder()
        
    
    settings = running_config()
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description='An opensource application for monitoring Datasources',
        debug=settings.DEBUG,
        lifespan=life_span
    )
    
    return app
        
    
    
    
    
        
        
        
        
        
    
    
    
    
    
    
    
    
    
    
    
    















