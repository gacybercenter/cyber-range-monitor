

from typing import TypeVar

from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.infrastructure.repos import SqlRepository
from range_monitor.infrastructure.security.crypto import Encryptor

from .models import (
    DataSource,
    GuacamoleDataSource,
    OpenStackDataSource,
    SaltStackDataSource,
)

D = TypeVar('D', bound=DataSource)


class DataSourceRepository(SqlRepository[D]):
    def __init__(self, session: AsyncSession, model: type[D]) -> None:
        super().__init__(session, model)
        self.encryptor = Encryptor()


    async def get_by_id(self, id: str) -> D | None:
        return await self.first(select(self.model).where(self.model.id == id))

    def get_enabled(self) -> Select:
        return select(self.model).where(self.model.enabled.is_(True))

    async def toggle(self, selected_datasource: D) -> D | None:
        if selected_datasource.enabled:
            return None

        statement = (
            update(self.model)
                .where(self.model.id != selected_datasource.id)
                .values(enabled=False)
        )
        await self._session.execute(statement)
        selected_datasource.enabled = not selected_datasource.enabled
        await self.sync_db(commit=True, refresh=True)
        return selected_datasource

    def prepare_obj_in(self, obj_in: dict) -> dict:
        if 'password' in obj_in:
            obj_in['password'] = self.encryptor.encrypt_string(obj_in['password'])
        return obj_in

    async def get_connection_params(self, id: str | None = None) -> dict | None:
        if not id:
            params = await self.get_mapping(self.get_enabled())
        else:
            params = await self.get_mapping(
                select(self.model).where(self.model.id == id)
            )

        if not params:
            return None

        params['password'] = self.encryptor.decrypt_string(params['password'])

        return params

    async def create_datasource(self, obj_in: dict) -> D:
        obj_in = self.prepare_obj_in(obj_in)
        created_model = await self.create(obj_in)
        return created_model

    async def update_datasource(self, to_update: D, obj_in: dict) -> D:
        obj_in = self.prepare_obj_in(obj_in)
        updated_model = await self.update(to_update, obj_in)
        return updated_model

    async def delete_by_id(self, id: str) -> bool:
        datasource = await self.get_by_id(id)
        if not datasource:
            return False

        return await self.delete(datasource)




GuacamoleRepo = DataSourceRepository[GuacamoleDataSource]
OpenStackRepo = DataSourceRepository[OpenStackDataSource]
SaltStackRepo = DataSourceRepository[SaltStackDataSource]
