from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from multiprocessing.reduction import register

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app import config
from fastapi.responses import JSONResponse

from app.db.core import connect_db


from app.redis.connection import RedisConnection

from app.misc.logging import APILogging

from app.middleware import (
    RequestLoggingMiddleware,
    SecurityHeaderMiddleware,
    SecurityHeaderOptions,
    request_validation_error_handler,
    http_exception_handler
)


# NOTE: in both on_startup, on_shutdown the app instance must be included
# even if it is not used to match method signature


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator[None, None]:
    '''Defines what should happen when the app first starts and when it shuts down
    the app start routine is before the "yield" and the shutdown routine is after the "yield"

    Arguments:
        app {FastAPI} -- the app instance, required even if not used
    '''

    app_logger = APILogging.setup()
    
    
    app_logger.info('Connecting to database...')
    
    await connect_db()
    
    app_logger.info('Database connected, connecting to redis...')
    
    await RedisConnection.connect()
    
    app_logger.info('Redis connected, API startup finished.')
    # ^ app startup
    yield
    # v app shutdown
    app_logger.info('Shutting down API, disconnecting Redis Connection...')
    
    await RedisConnection.disconnect()
    
    app_logger.info('Redis disconnected, ending API shutdown.')



def register_middleware(app: FastAPI) -> None:
    '''adds middleware to the API instance

    Arguments:
        app {FastAPI} -- the app
    '''
    cors = config.get_config_yml().cors
    app.add_middleware(
        CORSMiddleware,
        **cors.model_dump()
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        SecurityHeaderMiddleware,
        options=SecurityHeaderOptions()
    )


def register_exception_handlers(app: FastAPI) -> None:
    '''registers the exception handlers for the API

    Arguments:
        app {FastAPI} -- the app instance
    '''
    @app.exception_handler(RequestValidationError)
    async def handle_validation_exc(request, exc: RequestValidationError) -> JSONResponse:
        return await request_validation_error_handler(request, exc)
    
    @app.exception_handler(HTTPException)
    async def handle_http_exc(request, exc: HTTPException) -> JSONResponse:
        return await http_exception_handler(request, exc)  