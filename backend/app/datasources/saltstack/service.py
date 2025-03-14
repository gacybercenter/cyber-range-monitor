from sqlalchemy.ext.asyncio import AsyncSession


from app.datasources.base.service import DatasourceService
from .model import Saltstack
from .schema import (
    SaltstackCreateForm,
    SaltstackListResponse,
    SaltstackRead,
    SaltstackUpdateForm
)


class SaltstackService(DatasourceService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Saltstack, db)

    async def test_connection(self, id: int) -> None:
        pass
