from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from app.config import running_config



settings = running_config()

def register_middleware(app: FastAPI) -> None:
    from .exc_handler import register_exc_handlers
    from .request_log import RequestLoggingMiddleware
    from .security_headers import SecureHeadersMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if settings.USE_SECURITY_HEADERS:
        app.add_middleware(SecureHeadersMiddleware)  # type: ignore
    app.add_middleware(RequestLoggingMiddleware)  # type: ignore
    register_exc_handlers(app)

__all__ = ['register_middleware']