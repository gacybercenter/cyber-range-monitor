from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import PkIDModelMixin


class DatasourceMixin(PkIDModelMixin):
    """The shared mapped_columns for all of the Datasource models"""
    username: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
