from fastapi import FastAPI
from api.config.settings import app_config
import api.build as build

# Entry point / package for the API

app = FastAPI(
    title=app_config.TITLE,
    version='1.0.0',
    docs_url='/docs',
    debug=True,
    lifespan=build.life_span
)

build.register_middleware(app)
build.register_routes(app)