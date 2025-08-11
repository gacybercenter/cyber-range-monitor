from .service import OpenstackSourceService
from .schema import create_openstack_annotation


from ..interface.routes import create_datasource_router


open_stack_router = create_datasource_router(
    annotations=create_openstack_annotation(), service=OpenstackSourceService
)
