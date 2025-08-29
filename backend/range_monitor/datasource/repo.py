from sqlalchemy import update

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.datasource.model import DataSource, DataSourceType
from range_monitor.errors import ResourceNotFound, UnprocessableEntity


class DataSourceRepo(SqlRepo[DataSource]):
    model = DataSource

    async def enable_by_id(
        self, datasource_id: str, datasource_type: DataSourceType
    ) -> DataSource:
        if not (target := await self.get(datasource_id)):
            raise ResourceNotFound('Data source not found.')

        if target.type != datasource_type:
            raise UnprocessableEntity('This datasource does not match the given type.')

        if target.enabled:
            return target

        target.enabled = True

        stmnt = (
            update(DataSource)
            .where(
                DataSource.id != datasource_id,
                DataSource.type == datasource_type,
            )
            .values(enabled=False)
        )
        await self.db.execute(stmnt)
        await self.db.commit()
        await self.db.refresh(target)
        return target

    async def delete_by_id(
        self, datasource_id: str, expected_type: DataSourceType
    ) -> None:
        if not (target := await self.get(datasource_id)):
            raise ResourceNotFound('Data source not found.')

        if target.type != expected_type:
            raise UnprocessableEntity('This datasource does not match the given type.')

        await self.delete(target)
