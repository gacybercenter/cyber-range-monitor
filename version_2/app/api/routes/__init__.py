from fastapi import APIRouter


from .user_routes import user_router
from ...routes.api.auth_routes import auth_router
from .datasource_routes import init_datasource_routes


def register_routes(api_router: APIRouter) -> None:
    datasource_router = init_datasource_routes()
    for routes in (user_router, auth_router, datasource_router):
        api_router.include_router(routes)
