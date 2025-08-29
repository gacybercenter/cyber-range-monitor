


from range_monitor.core.sql_repo import SqlRepo
from range_monitor.datasource.service import DataSourceService
from range_monitor.open_stack.model import OpenStack
from range_monitor.open_stack.schema.datasource import OpenStackResponse
from range_monitor.open_stack.schema.spec import OpenStackConnectionSpec


class OpenStackRepo(SqlRepo[OpenStack]):
    model = OpenStack


class OpenStackSourceService(DataSourceService[
    OpenStackRepo,
    OpenStackResponse,
    OpenStackConnectionSpec,
]):
    response_schema = OpenStackResponse
    spec = OpenStackConnectionSpec