from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.domain.domains.datasource.repo import DataSourceRepository

from .model import SaltStackDataSource


class SaltStackRepo(DataSourceRepository[SaltStackDataSource]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SaltStackDataSource)