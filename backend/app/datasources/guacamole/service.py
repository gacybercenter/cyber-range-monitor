
from sqlalchemy.ext.asyncio import AsyncSession

from guacamole import session


from app.datasources.base.service import DatasourceService
from .model import Guacamole
from .schema import (
    GuacamoleCreateForm,
    GuacamoleListResponse,
    GuacamoleRead,
    GuacamoleUpdateForm
)


class GuacamoleService(DatasourceService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Guacamole, db)

    async def test_connection(self, id: int) -> bool:
        guac: Guacamole = await self.get_by_id(id)  # type: ignore
        plain_password = await self.read_datasource_password(guac)
        try:
            session(
                host=guac.endpoint,
                username=guac.username,
                password=plain_password,
                data_source=guac.datasource,
            )
            return True
        except Exception as e:
            return False
