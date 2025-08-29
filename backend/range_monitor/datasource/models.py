
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class DataSource:
    __abstract__ = True


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