from openstack import connection
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.data_sources.interface import DatasourceService
from server.app.data_sources.schemas import OpenstackPage, OpenstackSchema
from server.external.adapters import OpenstackAdapter
from server.external.openstack_client import OpenstackClient
from server.models import Openstack
from server.utils.paginate import PageParams


class OpenstackService(DatasourceService[Openstack, connection.Connection]):
    model = Openstack

    def __init__(
        self,
        db: AsyncSession,
        *,
        openstack_tenant: OpenstackClient,
    ) -> None:
        adapter = OpenstackAdapter(openstack_tenant)
        super().__init__(db, adapter=adapter)

    def serialize(self, instance: Openstack) -> OpenstackSchema:
        return OpenstackSchema.convert(instance)

    async def list_datasources(self, page: PageParams) -> OpenstackPage:
        models, total = await self.sources.get_data_sources(
            limit=page.page_size,
            offset=page.offset,
            converter=OpenstackSchema.convert,
        )
        page_info = OpenstackPage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )
        return OpenstackPage(page=page_info, data=models)  # type: ignore
