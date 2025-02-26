from fastapi import APIRouter, FastAPI


def register_routers(app: FastAPI) -> None:
    from .logs import log_router
    from .user import user_router
    from .auth import auth_router
    from .datasource import create_datasource_router

    datasource_router = create_datasource_router()
    ROUTERS: list[APIRouter] = [
        log_router,
        user_router,
        auth_router,
        datasource_router
    ]

    for router in ROUTERS:
        app.include_router(router)
