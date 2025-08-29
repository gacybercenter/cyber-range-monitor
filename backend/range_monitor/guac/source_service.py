
from api.domains.datasource.crud import (
    DataSourceRepository,
)

from range_monitor.errors import HTTPBadRequest, HTTPNotFound
from range_monitor.domain.schemas.datasource import DataSourceCreateModel, DataSourceModel


async def create_datasource(
    repo: DataSourceRepository,
    obj_in: DataSourceCreateModel,
    *,
    model_out: type[DataSourceModel] = DataSourceModel,
) -> DataSourceModel:
    new_ds = await repo.create(obj_in.dump())
    return model_out.convert(new_ds)


async def update_datasource(
    repo: DataSourceRepository,
    datasource_id: str,
    *,
    params: DataSourceCreateModel,
    model_out: type[DataSourceModel] = DataSourceModel,
) -> DataSourceModel:
    if not (existing := await repo.get_by_id(datasource_id)):
        raise HTTPNotFound('Datasource to update')

    if not (update_args := params.dump()):
        raise HTTPBadRequest('No update parameters provided')

    updated = await repo.update(existing, update_args)
    return model_out.convert(updated)

async def toggle_datasource(
    repo: DataSourceRepository,
    datasource_id: str,
    *,
    model_out: type[DataSourceModel] = DataSourceModel,
) -> DataSourceModel:
    if not (pressed_datasource := await repo.get_by_id(datasource_id)):
        raise HTTPNotFound('Datasource to toggle')

    toggled = await repo.toggle(pressed_datasource)
    if not toggled:
        raise HTTPBadRequest('Cannot toggle an already enabled datasource')

    return model_out.convert(toggled)

async def delete_datasource(repo: DataSourceRepository, datasource_id: str) -> None:
    if not (existing := await repo.get_by_id(datasource_id)):
        raise HTTPNotFound('Datasource to delete')

    if not await repo.delete(existing):
        raise HTTPBadRequest('Failed to delete the datasource')

