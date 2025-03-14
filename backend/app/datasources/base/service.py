from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.controller import CRUDController, ModelT

from app.extensions.security import crypto

from .model import DatasourceMixin
from .errors import (
    DatasourceNotFound,
    DatasourceToggleError,
    InvalidDatasourceSchema
)

DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")


class DatasourceService(CRUDController[ModelT]):
    """The base service class for all datasources"""

    def __init__(self, db_model: type[ModelT], db: AsyncSession) -> None:
        self.model = db_model
        self.db = db

    async def get_all_models(self) -> list[ModelT]:
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
        return sources # type: ignore[return-value]

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
        source = await self.get_by(self.model.id == id, self.db) # type: ignore
        if not source:
            raise DatasourceNotFound()
        return source

    async def enable_by_id(self, datasource_id: int) -> ModelT:
        """enables a datasource in the database; the selected datasource cannot be
        disabled

        Arguments:
            db {AsyncSession}
            datasource_id {int} id of the datasource to enable
        """
        pressed_datasource = await self.get_by_id(datasource_id)
        if pressed_datasource.enabled: # type: ignore
            raise DatasourceToggleError('Datasource is already enabled')

        previously_enabled = await self.get_enabled_source()
        if previously_enabled:
            previously_enabled.enabled = False

        pressed_datasource.enabled = True # type: ignore
        await self.db.commit()
        await self.db.refresh(pressed_datasource)
        return pressed_datasource # type: ignore

    async def get_enabled_source(self) -> DatasourceMixin | None:
        """returns the enabled datasource

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        """
        return await self.get_by(self.model.enabled.is_(True), self.db) # type: ignore

    async def create_datasource(
        self, obj_in: dict, db: AsyncSession
    ) -> DatasourceMixin:
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
            raise InvalidDatasourceSchema(
                "You must provide a password for the datasource")

        obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        return await self.create(db, obj_in) # type: ignore

    async def update_datasource(
        self, datasource: DatasourceMixin, obj_in: dict
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
        if "password" in obj_in:
            obj_in["password"] = crypto.encrypt_data(obj_in["password"])

        return await self.update(self.db, datasource, obj_in) # type: ignore

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
