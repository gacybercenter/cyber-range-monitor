


from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.datasource.model import DataSource, DataSourceType


class Guacamole(DataSource):
    __tablename__ = 'datasource_guacamole'

    id: Mapped[str] = mapped_column(
        ForeignKey('datasource.id', ondelete='CASCADE'),
        primary_key=True
    )

    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    datasource: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        unique=True,
    )

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.GUACAMOLE,
    }
