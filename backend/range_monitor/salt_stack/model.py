


from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from range_monitor.datasource.model import DataSource
from range_monitor.datasource.types import DataSourceType


class SaltStack(DataSource):

    id: Mapped[str] = mapped_column(
        ForeignKey('datasource.id', ondelete='CASCADE'),
        primary_key=True,
        use_existing_column=True,
    )

    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    hostname: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    __mapper_args__ = {
        'polymorphic_identity': DataSourceType.SALTSTACK,
    }
