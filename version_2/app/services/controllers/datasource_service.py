from typing import TypeVar, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ...common.crud_mixin import CRUDService
from app.models.mixins import DatasourceMixin

DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")

class DatasourceService(CRUDService[DatasourceMixin]):
    def __init__(self, db_model: Type[DatasourceMixin]) -> None:
        super().__init__(db_model)

    async def enable_datasource(self, db: AsyncSession, datasource_id: int) -> tuple:
        '''
        enables a datasource in the database; the selected datasource cannot be 
        disabled 

        Arguments:
            db {AsyncSession} 
            datasource_id {int} id of the datasource to enable
        Returns:
            tuple -- (was_successful: bool, error_message: str)
        '''
        pressed_datasource = await self.get_by(
            self.model.id == datasource_id,
            db
        )
        if pressed_datasource is None:
            return (False, 'Datasource not found')

        if pressed_datasource.enabled:
            return (False, 'Datasource already enabled')

        previously_enabled = await self.get_enabled(db)
        if previously_enabled:
            previously_enabled.enabled = False 

        pressed_datasource.enabled = True  # type: ignore
        await db.commit()
        await db.refresh(pressed_datasource)
        
        return (True, None)

    async def get_enabled(self, db: AsyncSession) -> Optional[DatasourceMixin]:
        '''
        returns the enabled datasource

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        '''
        return await self.get_by(self.model.enabled.is_(True), db)