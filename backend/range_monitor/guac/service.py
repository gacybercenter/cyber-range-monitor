


from range_monitor.datasource.repos import (
    Guacamole,
    GuacamoleRepo,
)
from range_monitor.datasource.service import DatasourceService
from range_monitor.guac.schema.orms import GuacamolePage, GuacamoleResponse
from range_monitor.params import PageParams


class GuacamoleDatasourceService(DatasourceService[Guacamole, GuacamoleResponse]):
    repo_class = GuacamoleRepo
    response_model = GuacamoleResponse



    async def list_datasources(
        self,
        page_params: PageParams,
        enabled: bool | None = None,
        label_search: str | None = None,
    ) -> GuacamolePage:
        sql_query = await self.repo.filter_by(
            enabled=enabled,
            label_search=label_search
        )

        query = page_params.paginate(sql_query.statement)

        results = []
        async for orm in self.repo.read.stream_scalars(query):
            results.append(self.response_model.convert(orm))

        return GuacamolePage.from_results(
            data=results,
            page_number=page_params.page_number,
            page_size=page_params.page_size,
            total=sql_query.total
        )