from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from range_monitor.middleware.access_log import AccessMiddleware
from range_monitor.middleware.config import CorsConfig
from range_monitor.middleware.request_id import RequestIdMiddleware


def register_middleware(app: FastAPI, cors: CorsConfig) -> None:
    '''
    Registers all middleware to the FastAPI instance,
    NOTE: the order of middleware registration matters,
    and CorrelationIdMiddleware should always be first.

    Parameters
    ----------
    app : FastAPI
    cors : CorsConfig
    '''
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.allow_origins,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
        allow_credentials=cors.allow_credentials,
    )
    app.add_middleware(AccessMiddleware)

