from typing import Any, Optional, TypeVar


from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.controller import CRUDController, ModelT

from app.extensions.security import crypto

from app.extensions.datasources.schema import DatasourceConnectionModel

from .model import DatasourceMixin
from .errors import (
    DatasourceNotFound,
    DatasourceToggleError,
    InvalidDatasourceSchema,
    NoEnabledDatasourceError
)

DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")


class DatasourceController(CRUDController[ModelT]):
    """The base controller class for all datasources"""

    def __init__(self, db_model: type[ModelT], db: AsyncSession) -> None:
        self.model = db_model
        self.db = db
        
    async def connect_args(self, source: Any) -> Any:
        raise NotImplementedError

    async def get_all_sources(self) -> list[ModelT]:
        '''gets all of the datasource models in the database

        Arguments:
            db {AsyncSession} -- the database session

        Raises:
            DatasourceNotFound: if no datasources are found in the database

        Returns:
            list[DatasourceMixin] -- the list of datasources retrieved
        '''
        sources = await self.get_all(self.db)
        if not sources or len(sources) == 0:
            raise DatasourceNotFound()
        return sources  # type: ignore[return-value]

    async def get_by_id(self, id: int) -> ModelT:
        '''gets a datasource by it's ID, raises 404 if not found

        Arguments:
            db {AsyncSession} -- the DB session
            id {int} -- the ID of the datasource

        Raises:
            DatasourceNotFound: if not found

        Returns:
            DatasourceMixin -- the ORM instance
        '''
        source = await self.get_by(self.model.id == id, self.db)  # type: ignore
        if not source:
            raise DatasourceNotFound()
        return source

    async def toggle_by_id(self, datasource_id: int) -> ModelT:
        """enables a datasource in the database; the selected datasource cannot be
        disabled

        Arguments:
            db {AsyncSession}
            datasource_id {int} id of the datasource to enable
        """
        pressed_datasource: DatasourceMixin = await self.get_by_id(datasource_id) # type: ignore
        if pressed_datasource.enabled:  
            raise DatasourceToggleError('Datasource is already enabled')

        await self.db.execute(
            update(self.model).values(enabled=False)
        )
        pressed_datasource.enabled = True
        await self.db.commit()
        await self.db.refresh(pressed_datasource)
        return pressed_datasource  # type: ignore

    async def get_enabled_source(self) -> ModelT | Any:
        """returns the enabled datasource

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        """
        return await self.get_by(self.model.enabled.is_(True), self.db)  # type: ignore

    async def create_datasource(self, obj_in: dict) -> DatasourceMixin:
        """Given a dictionary of the kwargs to create a datasource, the datasource
        is created and the password is encrypted before being saved to the database

        Arguments:
            obj_in {dict} -- the "model_dump" of the datasource
            db {AsyncSession}

        Raises:
            BadRequest: the password was not in the request

        Returns:
            DatasourceMixin
        """
        if "password" not in obj_in:
            raise InvalidDatasourceSchema("You must provide a password for the datasource")
        obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        return await self.create(self.db, obj_in)  # type: ignore

    async def update_by_id(
        self, datasource_id: int, obj_in: dict
    ) -> DatasourceMixin:
        """Given a datasource ORM instance and a dictionary of the kwargs to update
        the datasource, the datasource is updated and the password is encrypted before
        being saved to the database

        Arguments:
            db {AsyncSession}
            datasource {DatasourceMixin}
            obj_in {dict}

        Raises:
            BadRequest: the password was not in the request

        Returns:
            DatasourceReadBase -- _description_
        """
        if 'enabled' in obj_in:
            del obj_in['enabled']
        target_datasource = await self.get_by_id(datasource_id)
        if "password" in obj_in:
            obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        return await self.update(self.db, target_datasource, obj_in)  # type: ignore

    async def delete_by_id(self, datasource_id: int) -> None:
        target_datasource = await self.get_by_id(datasource_id)
        await self.delete(self.db, target_datasource)  # type: ignore
    
    async def connect(self, config: DatasourceConnectionModel) -> Any:
        raise NotImplementedError
    
        
    async def read_datasource_password(self, datasource_orm: DatasourceMixin) -> str:
        """Gets the decrypted password from a datasource ORM instance, only should be accesible to admins
        updating datasources or for connecting to the datasource
        Arguments:
            datasource_orm {DatasourceMixin}
        Returns:
            str -- the decrypted password
        """
        decrypted_password = crypto.decrypt_data(datasource_orm.password)
        return decrypted_password

    async def protected_read(self, id: int) -> tuple[ModelT, str]:
        '''returns a datasource with protected fields
        Arguments:
            id {int} -- the ID of the datasource to read
        Returns:
            Datasource, Password -- the datasource with protected fields and the password
        '''
        source = await self.get_by_id(id)
        plain_pwd = await self.read_datasource_password(source)  # type: ignore
        return source, plain_pwd
    
    
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    