from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import PkIDModelMixin


class DatasourceMixin(PkIDModelMixin):
    """The shared attributes for all of the Datasource models"""
    username: Mapped[str] = mapped_column(String, nullable=False, index=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
