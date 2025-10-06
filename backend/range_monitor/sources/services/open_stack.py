from openstack import connection
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.infra.security._crypto import CryptoService
from range_monitor.infra.adapters import OpenstackTenant
from range_monitor.schema.params import PageParams
from range_monitor.sources.adapters import OpenstackAdapter
from range_monitor.sources.models import Openstack
from range_monitor.sources.schemas import OpenstackPage, OpenstackSchema
from range_monitor.sources.services._service_abc import DatasourceService


class OpenstackService(DatasourceService[Openstack, connection.Connection]):
    model = Openstack

    def __init__(
        self,
        db: AsyncSession,
        *,
        crypto_service: CryptoService,
        openstack_tenant: OpenstackTenant
    ) -> None:
        adapter = OpenstackAdapter(openstack_tenant)
        super().__init__(
            db,
            crypto_service=crypto_service,
            api_adapter=adapter
        )

    def serialize(self, instance: Openstack) -> OpenstackSchema:
        return OpenstackSchema.convert(instance)

    async def list_datasources(
        self,
        label: str | None,
        page: PageParams
    ) -> OpenstackPage:
        models, total = await self.sources.list_sources(
            label=label,
            limit=page.page_size,
            offset=page.offset,
            converter=OpenstackSchema.convert,
        )
        page_info = OpenstackPage.get_page_details(
            total_items=total,
            page_number=page.page_number,
            page_size=page.page_size,
        )
        return OpenstackPage(page=page_info, data=models) # type: ignore

