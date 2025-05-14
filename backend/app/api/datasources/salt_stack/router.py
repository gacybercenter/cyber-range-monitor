from ..salt_stack.schema import create_saltstack_annotation
from ..salt_stack.service import SaltstackSourceService

from ..interface.routes import create_datasource_router


salt_stack_router = create_datasource_router(
    annotations=create_saltstack_annotation(), service=SaltstackSourceService
)
