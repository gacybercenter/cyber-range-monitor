from fastapi import APIRouter, FastAPI

from app.extensions import api_console


def register_routers(app: FastAPI) -> None:
    from .auth import auth_router
    from .datasource import create_datasource_router
    from .logs import log_router
    from .user import user_router

    datasource_router = create_datasource_router()
    ROUTERS: list[APIRouter] = [
        auth_router,
        log_router,
        user_router,
        datasource_router
    ]

    for router in ROUTERS:
        api_console.debug(f'Adding Router -> {router.prefix}')
        app.include_router(router)
