from fastapi import FastAPI




def register_routers(app: FastAPI) -> None:
    from .auth_router import auth_router
    from .datasource_router import initialize_router
    from .log_router import log_router
    
    
    ROUTERS = [
        auth_router,
        initialize_router(),
        log_router
    ]
    
    for routes in ROUTERS:
        app.include_router(routes)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    