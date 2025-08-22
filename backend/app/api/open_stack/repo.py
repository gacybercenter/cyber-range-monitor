

from sqlalchemy.ext.asyncio.session import AsyncSession

from app.api.domains.datasource.repo import DataSourceRepository


class OpenStackRepo(DataSourceRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, DataSourceRepository)



