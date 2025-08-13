import uuid
from datetime import UTC, datetime
from typing import Annotated

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

PrimaryKeyId = Annotated[
    int, mapped_column(autoincrement=True, primary_key=True, index=True, unique=True)
]

PrimaryUUIDKey = Annotated[
    str,
    mapped_column(
        String(100),
        primary_key=True,
        index=True,
        unique=True,
        default_factory=lambda: str(uuid.uuid4()),
    ),
]


def _now_utc_tz() -> datetime:
    return datetime.now(UTC)


class AuditedMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=_now_utc_tz, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=_now_utc_tz,
        onupdate=_now_utc_tz,
        nullable=False,
    )


class DatasourceMixin:
    id: Mapped[PrimaryKeyId] = mapped_column()

    username: Mapped[str] = mapped_column(String, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
