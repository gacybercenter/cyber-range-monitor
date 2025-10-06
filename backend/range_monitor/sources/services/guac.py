import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.sources.adapters import GuacamoleAdapter
from range_monitor.sources.models import Guacamole
from range_monitor.sources.schemas import GuacamolePage, GuacamoleSchema
from range_monitor.sources.services._service_abc import DatasourceService
from range_monitor.infra.security._crypto import CryptoService
from range_monitor.infra.adapters import APITenant
from range_monitor.schema.params import PageParams


class GuacamoleDatasourceService(DatasourceService[Guacamole, httpx.AsyncClient]):
    model = Guacamole

    def __init__(
        self,
        *,
        db: AsyncSession,
        crypto_service: CryptoService,
        guac_tenant: APITenant
    ) -> None:
        super().__init__(
            db,
            crypto_service=crypto_service,
            api_adapter=GuacamoleAdapter(guac_tenant),
        )

    def serialize(self, instance: Guacamole) -> GuacamoleSchema:
        return GuacamoleSchema.convert(instance)

    async def list_datasources(
        self,
        label: str | None,
        page: PageParams
    ) -> GuacamolePage:

        models, total = await self.sources.list_sources(
            label=label,
            limit=page.page_size,
            offset=page.offset,
            converter=GuacamoleSchema.convert
        )

        page_info = GuacamolePage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )

        return GuacamolePage(page=page_info, data=models) # type: ignore
