from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from .request_logger import RequestLoggingMiddleware
from .exc_handlers import register_exc_handlers
from .config import cors_settings


def register_middleware(app: FastAPI) -> None:
    '''Registers the middleware to the API instance

    Arguments:
        app {FastAPI} -- the API instance
    '''
    app.add_middleware(RequestLoggingMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.allow_origins,
        allow_headers=cors_settings.allow_headers,
        allow_credentials=cors_settings.allow_credentials,
        allow_methods=cors_settings.allow_methods
    )

    register_exc_handlers(app)
