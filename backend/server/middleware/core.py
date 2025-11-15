from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi.middleware.cors import CORSMiddleware

from server.middleware.access_log import AccessMiddleware
from server.middleware.correlation import CorrelationMiddleware

if TYPE_CHECKING:
    from fastapi import FastAPI

    from server.configs.toml import CorsConfig


def register_middleware(app: FastAPI, cors: CorsConfig) -> None:
    """
    Registers all middleware to the FastAPI instance,
    NOTE: the order of middleware registration matters,
    and CorrelationIdMiddleware should always be first.

    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance.
    cors : CorsConfig
        The CORS configuration.
    """
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors.allow_origins,
        allow_methods=cors.allow_methods,
        allow_headers=cors.allow_headers,
        allow_credentials=cors.allow_credentials,
    )
    app.add_middleware(AccessMiddleware)
