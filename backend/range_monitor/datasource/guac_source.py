


from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.domain.schemas.datasource import GuacamoleCreateModel

from .interface import DataSourceService
from .models import GuacamoleDataSource
from .repo import DataSourceRepository


class GuacamoleDataSourceService(DataSourceService[GuacamoleDataSource]):
    def __init__(
        self,
        db: AsyncSession
    ) -> None:
        super().__init__(
            DataSourceRepository[GuacamoleDataSource](db, GuacamoleDataSource)
        )

    async def create(self, obj_in: GuacamoleCreateModel) -> Any:
        return await self.repo.create(obj_in.dump())


