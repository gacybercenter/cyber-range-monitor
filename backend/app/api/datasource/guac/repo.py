
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.domains.datasource.repo import DataSourceRepository

from .model import GuacamoleDataSource


class GuacamoleRepo(DataSourceRepository[GuacamoleDataSource]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, GuacamoleDataSource)
        