from typing import Generic, List, TypeVar

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.security.crypto import CryptoUtils

from app.common.models import DatasourceMixin
from app.common.errors import HTTPBadRequest, HTTPNotFound
from app.common.repository import ModelRepository

DatasourceDB = TypeVar(
    'DatasourceDB',
    bound=DatasourceMixin
)


class DatasourceRepository(ModelRepository[DatasourceDB], Generic[DatasourceDB]):
    """The base service class for all datasources with the shared logic
    and operations. Refer to the DatasourceService for the methods that must
    be implemented by child classes.

    Arguments:
        Generic {DatasourceDB} -- the database model representing the datasource to 
        act on. (REQUIRED)
    """

    def __init__(
        self,
        *,
        model: type[DatasourceDB],
        db: AsyncSession,
        datasource_type: str
    ) -> None:
        '''Initializes the DatasourceRepository with the model and database 
        session.

        Args:
            model (type[DatasourceDB]): _the model to act on_
            db (AsyncSession): _the database_
            datasource_type (str): _the name of the datasource for error messages_
        '''
        super().__init__(model=model, db=db)
        self.datasource_type = datasource_type

    async def get_all_datasources(self) -> List[DatasourceDB]:
        sources = await self.select_all()
        return sources

    async def get_by_id(self, id: int) -> DatasourceDB:
        '''gets a datasource by it's ID, raises 404 if not found

        Arguments:
            db {AsyncSession} -- the DB session
            id {int} -- the ID of the datasource

        Raises:
            DatasourceNotFound: if not found

        Returns:
            DatasourceMixin -- the ORM instance
        '''
        source = await self.select(self.model.id == id)  # type: ignore
        if not source:
            raise HTTPNotFound(self.datasource_type)
        return source

    async def toggle(self, pressed_datasource: DatasourceDB) -> DatasourceDB:
        '''Toggles the datasource to be enabled or disabled, if the datasource is 
        already enabled a 400 error is raised since no datasource would be enabled
        breaking the plugin for all users.

        Arguments:
            pressed_datasource {DatasourceDB} -- the datasource to toggle

        Raises:
            HTTPBadDatasourceToggle: if the datasource is already enabled

        Returns:
            DatasourceDB -- the updated datasource
        '''
        if pressed_datasource.enabled:
            raise HTTPBadRequest(
                f'{pressed_datasource.username} '
                'is already enabled and cannot be toggled'
            )

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

    async def get_enabled(self) -> DatasourceDB | None:
        return await self.select(self.model.enabled.is_(True))

    async def create_datasource(self, flattened_obj_in: dict) -> DatasourceDB:
        if not "password" in flattened_obj_in:  # sanity check
            raise HTTPBadRequest(
                "You must provide a password for the datasource"
            )

        flattened_obj_in["password"] = CryptoUtils.encrypt(
            flattened_obj_in["password"]
        )

        created_model = await self.create(flattened_obj_in)
        return created_model

    async def update_datasource(
        self,
        to_update: DatasourceDB,
        flattened_obj_in: dict
    ) -> DatasourceDB:
        if not flattened_obj_in:
            raise HTTPBadRequest(
                'You must provide at least one field to update a datasource'
            )

        if "password" in flattened_obj_in:
            flattened_obj_in["password"] = CryptoUtils.encrypt(
                flattened_obj_in["password"]
            )

        updated_model = await self.update(to_update, flattened_obj_in)
        return updated_model

    async def read_password(self, datasource: DatasourceDB) -> str:
        return CryptoUtils.decrypt(datasource.password)
