from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    from .log_router import log_router
    from .user_router import user_router
    from .auth_router import auth_router
    from .datasource_router import create_datasource_routers

    datasource_router = create_datasource_routers()
    ROUTERS = [
        auth_router,
        user_router,
        log_router,
        datasource_router
    ]

    for router in ROUTERS:
        app.include_router(router)
