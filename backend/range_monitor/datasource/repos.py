

from types import MappingProxyType
from typing import Generic, TypeVar

from sqlalchemy import Select, Update, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from range_monitor.db.models.datasources import (
    Datasource,
    DatasourceCategory,
    Guacamole,
    OpenStack,
    SaltStack,
)
from range_monitor.db.repos.sql import SQLQuery, SQLReadRepository, SQLWriteRepository

D = TypeVar('D', bound=Datasource)


class BaseDatasourceRepo(Generic[D]):
    model: type[D]
    category: DatasourceCategory = DatasourceCategory.UNKNOWN

    def __init__(self, db: AsyncSession) -> None:
        self.read: SQLReadRepository[D] = SQLReadRepository(
            db,
            model=self.model
        )
        self.write: SQLWriteRepository[D] = SQLWriteRepository(
            db,
            model=self.model
        )
        self.db: AsyncSession = db

    async def label_exists(self, label: str) -> bool:
        '''
        Checks if a datasource with the given label exists.
        '''
        stmnt = select(self.model.id).where(self.model.label == label)
        return await self.read.first_dict(stmnt) is not None

    async def get_by_id(self, datasource_id: str) -> D | None:
        '''
        Retrieves a datasource by its ID.

        Parameters
        ----------
        datasource_id : str

        Returns
        -------
        T | None
        '''
        stmnt = select(self.model).where(self.model.id == datasource_id)
        return await self.read.scalar(stmnt)

    def _set_all_enabled(self, enabled: bool) -> Update:
        '''
        Returns an update statement to set all datasources to the given enabled status.
        '''
        return (
            update(self.model).
            where(self.model.enabled.is_(not enabled)).
            values(enabled=enabled)
        )


    async def enable(self, datasource: D) -> D | None:
        '''
        Enables the given datasource and disables all others.
        Returns None if the datasource is already enabled.

        Returns
        -------
        T | None
        '''

        if datasource.enabled:
            return None

        await self.db.execute(
            self._set_all_enabled(False)
        )
        datasource.enabled = True

        await self.write.save(commit=True)
        return datasource

    async def disable(self) -> bool:
        '''
        Disables all datasources.
        '''
        await self.db.execute(
            self._set_all_enabled(False)
        )
        return await self.write.save(commit=True)


    async def delete_by_id(self, datasource_id: str) -> bool:
        '''
        Deletes a datasource by its ID.

        Parameters
        ----------
        datasource_id : str

        Returns
        -------
        bool
            _False only if transaction failed or datasource not found.
        '''
        model = await self.get_by_id(datasource_id)
        if not model:
            return False

        return await self.write.delete(model)

    def add_filters(
        self,
        stmnt: Select,
        *,
        enabled: bool | None = None,
        label_search: str | None = None
    ) -> Select:
        if enabled is not None:
            stmnt = stmnt.where(Datasource.enabled.is_(enabled))

        if label_search is not None:
            clause = self.read.safelike(label_search, Datasource.label)
            stmnt = stmnt.where(clause)
        return stmnt

    async def filter_by(
        self,
        *,
        enabled: bool | None = None,
        label_search: str | None = None
    ) -> SQLQuery:

        stmnt = select(self.model).order_by(self.model.label)

        if self.category != DatasourceCategory.UNKNOWN:
            stmnt = stmnt.where(Datasource.category == self.category)

        stmnt = self.add_filters(
            stmnt,
            enabled=enabled,
            label_search=label_search
        )

        query = await self.read.new_query(stmnt)
        return query

    async def patch(self, datasource: D, params: dict) -> D | None:
        '''
        Updates a datasource by its ID and ensures label uniqueness.

        Parameters
        ----------
        datasource : T
        params : dict

        Returns
        -------
        T | None
        '''

        new_label = params.get('label')
        if new_label and new_label != datasource.label and await self.label_exists(
            new_label
        ):
            return None

        updated = await self.write.update(datasource, **params)

        return updated


class GuacamoleRepo(BaseDatasourceRepo[Guacamole]):
    model = Guacamole
    category = DatasourceCategory.GUACAMOLE


class OpenStackRepo(BaseDatasourceRepo[OpenStack]):
    model = OpenStack
    category = DatasourceCategory.OPENSTACK


class SaltStackRepo(BaseDatasourceRepo[SaltStack]):
    model = SaltStack
    category = DatasourceCategory.SALTSTACK

CategoryModelMap = MappingProxyType({
    DatasourceCategory.GUACAMOLE: Guacamole,
    DatasourceCategory.OPENSTACK: OpenStack,
    DatasourceCategory.SALTSTACK: SaltStack,
})

