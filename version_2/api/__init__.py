from fastapi import FastAPI
from api.config.settings import app_config
import api.build as build


app = FastAPI(
    title=app_config.TITLE,
    version='1.0.0',
    docs_url='/docs',
    debug=True,
    lifespan=build.life_span
)


@app.get('/')
async def read_root():
    return {'message': 'Hello World'}
