import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.data_sources.interface import DatasourceService
from server.app.data_sources.schemas import GuacamolePage, GuacamoleSchema
from server.external.adapters import ApiClient, GuacamoleAdapter
from server.models import Guacamole
from server.utils.paginate import PageParams


class GuacamoleDatasourceService(DatasourceService[Guacamole, httpx.AsyncClient]):
    model = Guacamole

    def __init__(self, *, db: AsyncSession, guac_tenant: ApiClient) -> None:
        adapter = GuacamoleAdapter(tenant=guac_tenant)
        super().__init__(db, adapter=adapter)

    def serialize(self, instance: Guacamole) -> GuacamoleSchema:
        return GuacamoleSchema.convert(instance)

    async def list_data_sources(
        self, label: str | None, page: PageParams
    ) -> GuacamolePage:
        models, total = await self.sources.get_data_sources(
            label=label,
            limit=page.page_size,
            offset=page.offset,
            converter=GuacamoleSchema.convert,
        )

        page_info = GuacamolePage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )

        return GuacamolePage(page=page_info, data=models)  # type: ignore
