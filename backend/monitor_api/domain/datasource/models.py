
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from monitor_api.infrastructure.model_mixins import PrimaryUUIDKey


class DataSource:
    __abstract__ = True

    id: Mapped[PrimaryUUIDKey] = mapped_column()

    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )

    password: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    endpoint: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )