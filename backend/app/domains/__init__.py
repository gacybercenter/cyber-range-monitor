

from fastapi import FastAPI


def register_api_routers(app: FastAPI) -> None:
    '''Adds the API Routers to the FastAPI instance

    Arguments:
        app {FastAPI} -- the app instance
    '''
    from .auth.router import auth_router
    from .datasources.router import ds_router
    from .users.router import user_router
    from .event_logs.router import log_router

    # change this when you add a router
    API_ROUTERS = [
        auth_router,
        ds_router,
        user_router,
        log_router
    ]
    for router in API_ROUTERS:
        app.include_router(router)


__all__ = [
    'register_api_routers'
]
