from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.extensions import api_console


def register_middleware(app: FastAPI, use_security_headers: bool) -> None:
    """adds middleware to the app instance

    Arguments:
        app {FastAPI} -- the app instance
        use_security_headers {bool} -- from the config.yml app.use_security_headers
    """
    from .exc_handler import register_exc_handlers
    from .request_log import RequestLoggingMiddleware
    from .security_headers import SecurityHeadersMiddleware

    api_console.debug("Registering CORS middleware...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if use_security_headers:
        api_console.debug("Registering security headers middleware...")
        app.add_middleware(SecurityHeadersMiddleware)  # type: ignore
    api_console.debug("Registering request logging middleware...")
    app.add_middleware(RequestLoggingMiddleware)  # type: ignore
    api_console.debug("Registering exception handlers...")
    register_exc_handlers(app)


__all__ = ["register_middleware"]
