from fastapi import FastAPI
from rich.traceback import install


from api.core.config import settings
import api.core.app_builder as app_builder

install(show_locals=True)


app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL,
    openapi_url=settings.OPENAPI_URL,
    debug=settings.DEBUG,
    lifespan=app_builder.life_span
)

app_builder.register_middleware(app)
app_builder.register_routes(app)
