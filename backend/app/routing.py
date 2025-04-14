from fastapi import FastAPI


def register_routers(app: FastAPI) -> None:
    '''adds all of the routers to the app instance 

    Arguments:
        app {FastAPI} -- the app to add the routers to 
    '''
    from app.users.router import user_router
    from app.auth.router import auth_router
    from app.event_logs.router import log_router
    from app.datasource.router import create_datasource_router

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(log_router)

    datasource_router = create_datasource_router()
    app.include_router(datasource_router)
