from fastapi import FastAPI




def register_routers(app: FastAPI) -> None:
    from .auth_router import auth_router
    from .datasource_router import initialize_router
    from .log_router import log_router
    from app.common.logging import LogWriter
    
    logger = LogWriter('ROUTES')
    
    ROUTERS = [
        auth_router,
        initialize_router(),
        log_router,
    ]
    
    for routes in ROUTERS:
        logger.debug(f'>> Registering router {routes.prefix}')
        app.include_router(routes)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    