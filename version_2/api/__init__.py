from fastapi import FastAPI
from api.config import settings
import api.build as build

# Entry point / package for the API

def create_app() -> None:
    app = FastAPI(
        title=settings.TITLE,
        version='1.0.0',
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