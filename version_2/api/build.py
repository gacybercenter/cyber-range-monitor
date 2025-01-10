from api.db.main import init_db
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.exceptions import HTTPException
from api.main import user
from api.utils.errors import handle_http_error, handle_validation_error


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator:
    print("Starting Application...")
    await init_db()
    yield
    print("Shutting Down Application...")


def register_exc_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc) -> Any:
        return handle_validation_error(exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc) -> Any:
        return handle_http_error(request, exc)


def register_routes(app: FastAPI) -> None:
    '''
    Registers all the routes from the APIRouters,
    all routers created must be registered here 

    Arguments:
        app {FastAPI} -- app instance 
    '''
    from api.main.user.routes import user_router
    from api.main.datasources.routes import init_datasource_routes

    # insert all routers here
    APP_ROUTES = [
        user_router,
        init_datasource_routes()
    ]
    for route in APP_ROUTES:
        print(f"[>] Registering {route.prefix} routes...")
        app.include_router(route)
