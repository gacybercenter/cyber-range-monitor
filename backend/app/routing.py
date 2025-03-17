from fastapi import APIRouter, FastAPI


def register_datasource_routers(app: FastAPI) -> None:
    '''creates the base datasource router and adds the datasource routers to it

    Arguments:
        app {FastAPI} -- the app to add the routers to
    '''
    from app.openstack_source.router import openstack_router
    from app.guacamole_source.router import guac_router
    # from app.saltstack_source.router import saltstack_router
    
    sources_router = APIRouter(prefix='/datasources')
    sources_router.include_router(openstack_router)
    sources_router.include_router(guac_router)
    app.include_router(sources_router)
    
    
    

def register_routers(app: FastAPI) -> None:
    '''adds all of the routers to the app instance 

    Arguments:
        app {FastAPI} -- the app to add the routers to 
    '''
    from app.users.router import user_router
    from app.auth.router import auth_router
    from app.logging.router import log_router
    # from app.datasources.router import create_datasource_router

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(log_router)
    register_datasource_routers(app)
    
    # datasource_router = create_datasource_router()
    # app.include_router(datasource_router)
