

from range_monitor.core.sql_repo import SqlRepo
from range_monitor.datasource.service import DataSourceService
from range_monitor.guac.model import Guacamole
from range_monitor.guac.schema.datasource import GuacamoleResponse
from range_monitor.guac.schema.spec import GuacamoleSessionSpec


class GuacamoleRepo(SqlRepo[Guacamole]):
    model = Guacamole


class GuacamoleSourceService(DataSourceService[
    GuacamoleRepo,
    GuacamoleResponse,
    GuacamoleSessionSpec,
]):
    response_schema = GuacamoleResponse
    spec = GuacamoleSessionSpec



