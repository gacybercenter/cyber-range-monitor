from typing import TypeVar, Generic, Type, List
from api.db.main import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


from api.models.mixins import DatasourceMixin
from api.db.service_wrapper import CRUDService


DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")
class DatasourceService(CRUDService[DatasourceMixin]):
    def __init__(self, db_model: Type[DatasourceMixin]) -> None:
        super().__init__(db_model)        
    
    async def enable_datasource(self, db: AsyncSession, datasource_id: int) -> tuple:
        '''enables a datasource in the database'''
        pressed_datasource = await self.get_by(
            self.model.id == datasource_id,
            db
        )
        if pressed_datasource is None:
            return (False, 'Datasource not found')
        
        if pressed_datasource.enabled:
            return (False, 'Datasource already enabled')
        
        pressed_datasource.enabled = True
        await db.execute(
            update(self.model).values(enabled=False)
        )
        await db.commit()
        await db.refresh(pressed_datasource)
        return (True, None)


    
    
    
    
    
    
    
    
    
    
    

        
        
        
        
        
        
        
            
    
        
        
        
        
        
        
        
        
        
    
    
        
        
    
    
    