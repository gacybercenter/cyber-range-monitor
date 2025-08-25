from sqlalchemy.ext.asyncio import AsyncSession

from monitor_api.domain.domains.datasource.repo import DataSourceRepository

from .model import SaltStackDataSource


class SaltStackRepo(DataSourceRepository[SaltStackDataSource]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SaltStackDataSource)