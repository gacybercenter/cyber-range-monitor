from fastapi import FastAPI
from api.config import set_settings, settings
import api.build as build
from api.config.builds import Settings
from typing import Optional


# Entry point / package for the API

def create_app(config: Optional[Settings] = None) -> None:
    set_settings(config)
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
        debug=settings.DEBUG,
        lifespan=build.life_span
    )
    build.register_middleware(app)
    build.register_routes(app)


if __name__ == '__main__':
    app = create_app()
