import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.infra.adapters import APITenant
from range_monitor.infra.security import CryptoService
from range_monitor.schema.params import PageParams
from range_monitor.sources.adapters import SaltstackAdapter
from range_monitor.sources.models import Saltstack
from range_monitor.sources.schemas import SaltstackPage, SaltstackSchema
from range_monitor.sources.services._service_abc import DatasourceService


class SaltstackService(DatasourceService[Saltstack, httpx.AsyncClient]):
    model = Saltstack

    def __init__(
        self, *, db: AsyncSession, crypto_service: CryptoService, salt_tenant: APITenant
    ) -> None:
        adapter = SaltstackAdapter(salt_tenant)
        super().__init__(db, crypto_service=crypto_service, api_adapter=adapter)

    def serialize(self, instance: Saltstack) -> SaltstackSchema:
        return SaltstackSchema.convert(instance)

    async def list_datasources(
        self, label: str | None, page: PageParams
    ) -> SaltstackPage:
        models, total = await self.sources.list_sources(
            label=label,
            limit=page.limit,
            offset=page.offset,
            converter=SaltstackSchema.convert,
        )

        page_info = SaltstackPage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )

        return SaltstackPage(page=page_info, data=models)  # type: ignore
