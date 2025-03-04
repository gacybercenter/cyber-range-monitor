from typing import Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.datasources.errors import DatasourceNotFound, DatasourceToggleError
from app.extensions.security import crypto
from app.models.datasource.datasource_mixin import DatasourceMixin
from app.shared.crud_mixin import CRUDService

DatasourceT = TypeVar("DatasourceT", bound="DatasourceMixin")


class DatasourceService(CRUDService[DatasourceMixin]):
    """The service for the datasource model"""

    def __init__(self, db_model: Type[DatasourceMixin]) -> None:
        super().__init__(db_model)

    async def enable_datasource(self, db: AsyncSession, datasource_id: int) -> None:
        """enables a datasource in the database; the selected datasource cannot be
        disabled

        Arguments:
            db {AsyncSession}
            datasource_id {int} id of the datasource to enable
        Returns:
            tuple -- (was_successful: bool, error_message: str)
        """
        pressed_datasource = await self.get_by(self.model.id == datasource_id, db)
        if pressed_datasource is None:
            raise DatasourceToggleError("Datasource not found")

        if pressed_datasource.enabled:
            raise DatasourceNotFound()

        previously_enabled = await self.get_enabled(db)
        if previously_enabled:
            previously_enabled.enabled = False

        pressed_datasource.enabled = True  # type: ignore
        await db.commit()
        await db.refresh(pressed_datasource)

    async def get_enabled(self, db: AsyncSession) -> Optional[DatasourceMixin]:
        """returns the enabled datasource

        Arguments:
            db {AsyncSession} -- the database session
        Returns:
            List[DatasourceMixin] -- list of enabled datasources
        """
        return await self.get_by(self.model.enabled.is_(True), db)

    async def create_datasource(self, obj_in: dict, db: AsyncSession) -> DatasourceMixin:
        """Given a dictionary of the kwargs to create a datasource, the datasource
        is created and the password is encrypted before being saved to the database

        Arguments:
            obj_in {dict} -- the "model_dump" of the datasource
            db {AsyncSession}

        Raises:
            BadRequest: the password was not in the request

        Returns:
            DatasourceMixin -- _description_
        """

        obj_in["password"] = crypto.encrypt_data(obj_in["password"])
        return await self.create(db, obj_in)

    async def update_datasource(
        self, db: AsyncSession, datasource: DatasourceMixin, obj_in: dict
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

        return await self.update(db, datasource, obj_in)

    async def get_datasource_password(self, datasource_orm: DatasourceMixin) -> str:
        """Gets the decrypted password from a datasource ORM instance

        Arguments:
            datasource_orm {DatasourceMixin}

        Returns:
            str
        """
        decrypted_password = crypto.decrypt_data(datasource_orm.password)
        return decrypted_password
