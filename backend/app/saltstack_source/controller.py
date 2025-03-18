from sqlalchemy.ext.asyncio import AsyncSession


from app.extensions.datasources.controller import DatasourceController
from .model import SaltstackSource
from .schema import (
    SaltstackCreateForm,
    SaltstackListResponse,
    SaltstackRead,
    SaltstackUpdateForm,
    SaltstackProtectedRead
)



class SaltstackController(DatasourceController):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(SaltstackSource, db)

    async def test_connection(self, id: int) -> None:
        pass

    async def protected_read(self, id: int) -> SaltstackRead:
        '''returns a Saltstack datasource with protected fields
        Arguments:
            id {int} -- the ID of the datasource to read
        Returns:
            SaltstackRead -- the Saltstack datasource with protected fields
        '''
        saltstack_src = await self.get_by_id(id)
        protected_schema = SaltstackProtectedRead.to_model(saltstack_src)
        protected_schema.password = await self.read_datasource_password(saltstack_src)
        return protected_schema

    async def get_all_sources(self) -> SaltstackListResponse:
        '''returns all the Saltstack datasources
        Returns:
            SaltstackListResponse -- the list of all the Saltstack datasources
        '''
        saltstack_sources = await super().get_all_sources()
        list_response = SaltstackListResponse.from_list(saltstack_sources)
        return list_response
