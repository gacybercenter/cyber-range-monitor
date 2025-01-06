from fastapi import FastAPI
from api.config.settings import app_config

app = FastAPI(
    title=app_config.TITLE,
    version='1.0.0',
    docs_url='/docs',
    debug=True
)


@app.get('/')
async def read_root():
    return {'message': 'Hello World'}
