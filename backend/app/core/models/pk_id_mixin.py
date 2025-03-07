from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column


class PkIDModelMixin:
    """generic model with an autoincremented ID thats a primary key"""

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, unique=True, index=True
    )
