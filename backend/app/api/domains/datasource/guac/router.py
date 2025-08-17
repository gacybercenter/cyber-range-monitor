from .schema import create_guac_annotation
from .service import GuacamoleSourceService


from ..interface.routes import create_datasource_router


guac_router = create_datasource_router(
    annotations=create_guac_annotation(),  # type: ignore
    service=GuacamoleSourceService,
)
