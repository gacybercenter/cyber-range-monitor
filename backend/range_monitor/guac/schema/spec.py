
from typing import TYPE_CHECKING

from range_monitor.core.pydantic import PydanticMixin
from range_monitor.datasource.specs import ConnectionSpec

if TYPE_CHECKING:
    from typing import Self

    from range_monitor.datasource.model import Guacamole


class GuacamoleSessionSpec(PydanticMixin, ConnectionSpec['Guacamole']):
    host: str
    data_source: str
    username: str
    password: str

    @classmethod
    def create_from_source(
        cls, datasource: 'Guacamole', plaintext_password: str
    ) -> Self:
        return cls(
            host=datasource.endpoint,
            data_source=datasource.datasource,
            username=datasource.username,
            password=plaintext_password,
        )
