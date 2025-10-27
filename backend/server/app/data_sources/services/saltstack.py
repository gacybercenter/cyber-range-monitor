import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.data_sources.interface import DatasourceService
from server.app.data_sources.schemas import SaltstackPage, SaltstackSchema
from server.external.adapters import SaltstackAdapter
from server.external.api_clients import ApiClient
from server.models import Saltstack
from server.utils.paginate import PageParams


class SaltstackService(DatasourceService[Saltstack, httpx.AsyncClient]):
    model = Saltstack

    def __init__(self, *, db: AsyncSession, salt_tenant: ApiClient) -> None:
        adapter = SaltstackAdapter(salt_tenant)
        super().__init__(db, adapter=adapter)

    def serialize(self, instance: Saltstack) -> SaltstackSchema:
        return SaltstackSchema.convert(instance)

    async def list_datasources(
        self, label: str | None, page: PageParams
    ) -> SaltstackPage:
        models, total = await self.sources.get_data_sources(
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
