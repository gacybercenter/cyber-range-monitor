from api.db.main import init_db
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI

from api.main import user


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator:
    print("Starting Application...")
    await init_db()
    yield
    print("Shutting Down Application...")


def register_routes(app: FastAPI) -> None:
    '''
    Registers all the routes from the APIRouters,
    all routers created must be registered here 

    Arguments:
        app {FastAPI} -- app instance 
    '''
    from api.main.user.user_routes import user_router
    from api.main.datasources.routes import create_datasource_router
    
    # insert all routers here
    APP_ROUTES = [
        user_router,
        create_datasource_router()
    ]
    for route in APP_ROUTES:
        print(f"[>] Registering {route.prefix} routes...")
        app.include_router(route)
    
    
    
    
