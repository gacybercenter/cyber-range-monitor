from fastapi import FastAPI
from rich.traceback import install


from api.config import settings
import api.build as build

install(show_locals=True)


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
