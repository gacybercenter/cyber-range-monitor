from api.db.main import init_db, get_session
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI
from api.db.logging import LogWriter
from api.middleware import register_exc_handlers, register_request_logging


# The functions for 'building' the application

logger = LogWriter('APPLICATION')


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator:
    '''
    Defines and initializes the context of the application,
    before the yield are the startup actions and anything after 
    defines how the application should shutdown

    Arguments:
        app {FastAPI} -- although not used, it is required by FastAPI
    Returns:
        AsyncGenerator -- _description_
    '''
    await init_db()

    async with get_session() as session:
        await logger.info("Build successful, application started", session)
        await session.close()

    # ^- app startup
    yield
    # v- app shutdown
    async with get_session() as session:
        await logger.info("Shutting down application...", session)
        await session.close()


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


def register_middleware(app: FastAPI) -> None:
    '''
    Registers the middleware functions for the app

    Arguments:
        app {FastAPI} -- app instance
    '''
    register_exc_handlers(app)
    register_request_logging(app)
