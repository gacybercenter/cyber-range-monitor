


from typing import Annotated

from fastapi import Depends

from range_monitor.datasource.repos import DataSourceRepo
from range_monitor.depends import DatabaseDep


async def get_datasource_repo(db: DatabaseDep) -> DataSourceRepo:
    return DataSourceRepo(db)


DataSourceRepoDep = Annotated[DataSourceRepo, Depends(get_datasource_repo)]
