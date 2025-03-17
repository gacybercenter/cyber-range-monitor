from fastapi import FastAPI
from rich.traceback import install


from app import build, routing 

install(show_locals=True)

def create_app() -> FastAPI:
    '''creates the fastapi app instance and adds the necessary configurations 
    Returns:
        FastAPI -- the fastapi app instance
    '''
    app = build.create_instance()
    build.handle_documentation(app)
    build.register_middleware(app)
    routing.register_routers(app)
    return app
