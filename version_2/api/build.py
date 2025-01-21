from api.db.main import init_db
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI
from pydantic import ValidationError
from fastapi.exceptions import HTTPException
from api.utils.errors import handle_http_error, handle_validation_error
from api.main.services.log_service import LogWriter


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator:
    await init_db()
    await LogWriter.info_log("API & Database is Ready")
    
    yield
    
    await LogWriter.info_log("Shutting Down Application...")
    print("Shutting Down Application...")


def register_exc_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request, exc) -> Any:
        await LogWriter.error_log(f'Intercepted a Validation Error: {exc}')
        return handle_validation_error(exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException) -> Any:
        await LogWriter.error_log(f'Intercepted an HTTP Error: {exc}')
        if exc.status_code == 500:
            await LogWriter.critical_log(f'INTERNAL SERVER ERROR OCCURED: {exc}')
        return handle_http_error(request, exc)

def register_routes(app: FastAPI) -> None:
    '''
    Registers all the routes from the APIRouters,
    all routers created must be registered here 

    Arguments:
        app {FastAPI} -- app instance 
    '''
    from api.main.routes import user_router, auth_router, init_datasource_routes
    from api.main.routes.datasource_routes import init_datasource_routes

    APP_ROUTES = [
        auth_router,
        user_router,
        init_datasource_routes()
    ]
    for route in APP_ROUTES:
        print(f"[>] Registering {route.prefix} routes...")
        app.include_router(route)
