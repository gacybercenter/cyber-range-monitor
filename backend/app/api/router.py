from fastapi import FastAPI
from .auth.router import auth_router
from .datasources.router import datasource_router
from .users.router import user_router


def register_routes(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(datasource_router)
    app.include_router(user_router)
