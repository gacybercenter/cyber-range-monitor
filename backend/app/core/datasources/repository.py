from email.policy import HTTP
from typing import Generic, List, TypeVar

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.security import crypto

from app.core.mixins.datasource import DatasourceMixin

from app.core.errors import (
    HTTPNotFound,
    
)

from .errors import HTTPBadDatasourceToggle, HTTPBadRequest, HTTPDatasourceNotFound

from ..interfaces.repository import ModelRepository

DSMixin = TypeVar('DSMixin', bound=DatasourceMixin)


class DatasourceRepository(ModelRepository[DSMixin], Generic[DSMixin]):
    """The base service class for all datasources with the shared logic
    and operations. Refer to the DatasourceService for the methods that must
    be implemented by child classes.

    Arguments:
        Generic {DSMixin} -- the database model representing the datasource to 
        act on. (REQUIRED)
    """

    def __init__(self, model: type[DSMixin], db: AsyncSession) -> None:
        super().__init__(model, db)

    async def get_all_datasources(self) -> List[DSMixin]:
        '''gets all of the datasource models in the database

        Arguments:
            db {AsyncSession} -- the database session

        Raises:
            DatasourceNotFound: if no datasources are found in the database

        Returns:
            list[DatasourceMixin] -- the list of datasources retrieved
        '''
        sources = await self.get_all()
        return sources

    async def get_by_id(self, id: int) -> DSMixin:
        '''gets a datasource by it's ID, raises 404 if not found

        Arguments:
            db {AsyncSession} -- the DB session
            id {int} -- the ID of the datasource

        Raises:
            DatasourceNotFound: if not found

        Returns:
            DatasourceMixin -- the ORM instance
        '''
        source = await self.get_by(self.model.id == id)  # type: ignore
        if not source:
            raise HTTPDatasourceNotFound(self.model.__name__)
        return source

    async def toggle(self, pressed_datasource: DSMixin) -> DSMixin:
        '''Toggles the datasource to be enabled or disabled, if the datasource is 
        already enabled a 400 error is raised since no datasource would be enabled
        breaking the plugin for all users.

        Arguments:
            pressed_datasource {DSMixin} -- the datasource to toggle

        Raises:
            HTTPBadDatasourceToggle: if the datasource is already enabled

        Returns:
            DSMixin -- the updated datasource
        '''
        if pressed_datasource.enabled:
            raise HTTPBadDatasourceToggle(pressed_datasource.username)
        stmnt = (
            update(self.model)
            .where(self.model.id != pressed_datasource.id)  # type: ignore
            .values(enabled=False)
        )
        await self.db.execute(stmnt)
        pressed_datasource.enabled = not pressed_datasource.enabled
        await self.db.commit()
        await self.db.refresh(pressed_datasource)
        return pressed_datasource

    async def get_enabled(self) -> DSMixin | None:
        """returns the enabled datasource or none if no datasource
        is enabled.

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        """
        return await self.get_by(self.model.enabled.is_(True))

    async def create_datasource(self, flattened_obj_in: dict) -> DSMixin:
        """given a dictionary of the kwargs to create a datasource, the datasource
        is created and the password is encrypted before being saved to the database
        additionally the _validate_schema method is called to validate the schema
        which not overriden simply serializes the schema

        Arguments:
            flattened_obj_in {dict} -- the "model_dump" of the datasource
            db {AsyncSession}

        Raises:
            BadRequest: the password was not in the request

        Returns:
            DatasourceReadModel -- the created datasource
        """
        if not "password" in flattened_obj_in:  # sanity check
            raise HTTPBadRequest(
                "You must provide a password for the datasource"
            )

        flattened_obj_in["password"] = crypto.encrypt_data(
            flattened_obj_in["password"]
        )
        created_model = await self.create(flattened_obj_in)
        return created_model

    async def update_datasource(
        self,
        model: DSMixin,
        flattened_obj_in: dict
    ) -> DSMixin:
        """Given a datasource ORM instance and a dictionary of the kwargs to update
        the datasource, the datasource is updated and the password is encrypted before
        being saved to the database

        Arguments:
            datasource {DatasourceMixin} - the datasource to update
            flattened_obj_in {dict} - the "model_dump" of the datasource

        Raises:
            BadRequest: the password was not in the request
        Returns:
            DatasourceReadModel -- the updated datasource
        """
        if not flattened_obj_in:
            raise HTTPBadRequest(
                'You must provide at least one field to update a datasource'
            )

        if "password" in flattened_obj_in:
            flattened_obj_in["password"] = crypto.encrypt_data(
                flattened_obj_in["password"]
            )

        updated_model = await self.update(model, flattened_obj_in)
        return updated_model

    async def read_password(self, datasource_orm: DSMixin) -> str:
        """Gets the decrypted password from a datasource ORM instance, only should be accesible to admins
        updating datasources or for connecting to the datasource
        Arguments:
            datasource_orm {DatasourceMixin}
        Returns:
            str -- the decrypted password
        """
        decrypted_password = crypto.decrypt_data(datasource_orm.password)
        return decrypted_password
