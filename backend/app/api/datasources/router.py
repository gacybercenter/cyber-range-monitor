from fastapi import APIRouter
from .guac.router import guac_router
from .open_stack.router import open_stack_router
from .salt_stack.router import salt_stack_router

datasource_router = APIRouter(
    prefix='/datasources',
    tags=['datasources']
)
datasource_router.include_router(
    guac_router,
    prefix='/guac',
    tags=['guac']
)
datasource_router.include_router(
    open_stack_router,
    prefix='/openstack',
    tags=['openstack']
)
datasource_router.include_router(
    salt_stack_router,
    prefix='/saltstack',
    tags=['saltstack']
)