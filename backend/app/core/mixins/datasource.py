from sqlalchemy import Boolean, String, Integer
from sqlalchemy.orm import Mapped, mapped_column


class DatasourceMixin:
    """The shared attributes for all of the Datasource models"""

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        unique=True,
        index=True
    )

    username: Mapped[str] = mapped_column(String, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
